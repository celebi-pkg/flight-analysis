"""
CLI commands for google-flight-analysis.

Provides individual command modules that can be imported separately.
"""

import sys
import json
import click
from typing import Optional


@click.command()
@click.argument("origin")
@click.argument("destination")
@click.option("--date", "-d", "departure_date", required=True, help="Departure date (YYYY-MM-DD)")
@click.option("--return-date", "-r", help="Return date for round-trip (YYYY-MM-DD)")
@click.option("--trip-type", type=click.Choice(["one-way", "round-trip"]), default="one-way")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def price(
    ctx: click.Context,
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str],
    trip_type: str,
    output_json: bool,
) -> None:
    """Get current flight price for a route."""
    from google_flight_analysis.scrape import scrape
    
    click.echo(f"Scraping flights from {origin} to {destination}...")
    
    try:
        result = scrape(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            trip_type=trip_type,
        )
        
        if output_json:
            data = result.data.to_dict(orient="records")
            click.echo(json.dumps(data, indent=2, default=str))
        else:
            click.echo(f"\nFound {result.num_flights} flights:")
            click.echo(result.data.to_string())
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument("origin")
@click.argument("destination")
@click.option("--date", "-d", "departure_date", required=True, help="Departure date (YYYY-MM-DD)")
@click.option("--return-date", "-r", help="Return date for round-trip")
@click.option("--trip-type", type=click.Choice(["one-way", "round-trip"]), default="one-way")
@click.option("--save/--no-save", default=True, help="Save results to database")
@click.pass_context
def scrape_cmd(
    ctx: click.Context,
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str],
    trip_type: str,
    save: bool,
) -> None:
    """Scrape and store flight data for a route."""
    from google_flight_analysis.scrape import scrape
    
    click.echo(f"Scraping flights from {origin} to {destination}...")
    
    try:
        result = scrape(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            trip_type=trip_type,
        )
        
        click.echo(f"Found {result.num_flights} flights")
        
        if save:
            count = result.save_to_db(db_path=ctx.obj.get("db_path"))
            click.echo(f"Saved {count} flights to database")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.command(name="db")
@click.argument("action", type=click.Choice(["init", "info", "routes", "history"]))
@click.option("--origin", "-o", help="Origin airport code")
@click.option("--destination", "-d", help="Destination airport code")
@click.option("--days", type=int, default=30, help="Number of days for history")
@click.pass_context
def db_cmd(
    ctx: click.Context,
    action: str,
    origin: Optional[str],
    destination: Optional[str],
    days: int,
) -> None:
    """Database operations."""
    from google_flight_analysis.db import get_db
    
    db = get_db(ctx.obj.get("db_path"))
    
    if action == "init":
        db.initdb()
        click.echo(f"Database initialized at {db.db_path}")
        
    elif action == "info":
        routes = db.get_active_routes()
        click.echo(f"Database: {db.db_path}")
        click.echo(f"Active routes: {len(routes)}")
        
    elif action == "routes":
        routes = db.get_active_routes()
        if not routes:
            click.echo("No active routes")
        else:
            for route in routes:
                click.echo(f"  {route.origin} -> {route.destination} ({route.trip_type.value})")
                
    elif action == "history":
        if not origin or not destination:
            click.echo("Error: --origin and --destination required", err=True)
            sys.exit(1)
        
        history = db.get_price_history(origin, destination, days)
        if not history:
            click.echo(f"No history found for {origin} -> {destination}")
        else:
            click.echo(f"Price history for {origin} -> {destination} (last {days} days):")
            for item in history:
                date = item.get("date", "N/A")
                min_p = item.get("min_price")
                avg_p = item.get("avg_price")
                click.echo(
                    f"  {date}: min=${min_p/100:.2f if min_p else 'N/A'}, "
                    f"avg=${avg_p/100:.2f if avg_p else 'N/A'}"
                )


@click.command()
@click.argument("origin")
@click.argument("destination")
@click.option("--departure-date", "-d", required=True, help="Departure date (YYYY-MM-DD)")
@click.option("--days-lookahead", type=int, default=7, help="Days to look ahead for prices")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def analyze_cmd(
    ctx: click.Context,
    origin: str,
    destination: str,
    departure_date: str,
    days_lookahead: int,
    output_json: bool,
) -> None:
    """Analyze prices for best buy day."""
    from google_flight_analysis.db import get_db
    
    db = get_db(ctx.obj.get("db_path"))
    
    history = db.get_price_history(origin, destination, days=days_lookahead)
    
    if not history:
        click.echo(f"No price history for {origin} -> {destination}")
        click.echo("Run scrape command first to collect data")
        return
    
    prices = [(h["date"], h["min_price"]) for h in history if h.get("min_price")]
    
    if not prices:
        click.echo("No prices found in history")
        return
    
    best_date, best_price = min(prices, key=lambda x: x[1])
    
    if output_json:
        output = {
            "origin": origin,
            "destination": destination,
            "best_date": best_date,
            "best_price_cents": best_price,
            "best_price_dollars": best_price / 100 if best_price else None,
        }
        click.echo(json.dumps(output, indent=2, default=str))
    else:
        click.echo(f"Best day to buy: {best_date}")
        if best_price:
            click.echo(f"Best price: ${best_price / 100:.2f}")


@click.command()
@click.argument("origin")
@click.argument("destination")
@click.option("--departure-date", "-d", required=True, help="Departure date (YYYY-MM-DD)")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def recommend(
    ctx: click.Context,
    origin: str,
    destination: str,
    departure_date: str,
    output_json: bool,
) -> None:
    """Recommend best flight option."""
    from google_flight_analysis.scrape import scrape
    
    try:
        result = scrape(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
        )
        
        df = result.data
        
        if df.empty:
            click.echo("No flights found")
            return
        
        if "price_cents" in df.columns:
            df = df.sort_values("price_cents")
            best = df.iloc[0]
            
            if output_json:
                output = {
                    "origin": origin,
                    "destination": destination,
                    "departure_date": departure_date,
                    "price": int(best.get("price_cents", 0)) if best.get("price_cents") else None,
                    "departure_time": best.get("departure_time"),
                    "arrival_time": best.get("arrival_time"),
                    "duration": best.get("duration"),
                    "stops": best.get("stops"),
                }
                click.echo(json.dumps(output, indent=2, default=str))
            else:
                click.echo(f"\nBest flight: {origin} -> {destination}")
                click.echo(f"  Date: {departure_date}")
                if best.get("price_cents"):
                    click.echo(f"  Price: ${best.get('price_cents') / 100:.2f}")
                click.echo(f"  Time: {best.get('departure_time', 'N/A')} - {best.get('arrival_time', 'N/A')}")
                click.echo(f"  Duration: {best.get('duration', 'N/A')}")
                click.echo(f"  Stops: {best.get('stops', 'N/A')}")
                
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)