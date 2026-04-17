"""Tests for configuration module."""

import pytest

from google_flight_analysis.config import (
    config as app_config,
    get_config,
    update_config,
    ChromeConfig,
    ScrapeConfig,
    DBConfig,
    Config,
)


class TestConfigClasses:
    """Test configuration classes."""
    
    def test_chrome_config_defaults(self):
        """Test ChromeConfig defaults."""
        cfg = ChromeConfig()
        
        assert "--no-sandbox" in cfg.options
        assert cfg.wait == 10
        assert cfg.page_load_timeout == 30
    
    def test_scrape_config_defaults(self):
        """Test ScrapeConfig defaults."""
        cfg = ScrapeConfig()
        
        assert cfg.max_retries == 3
        assert cfg.retry_delay == 2
        assert cfg.min_wait_between_requests == 5
    
    def test_db_config_defaults(self):
        """Test DBConfig defaults."""
        cfg = DBConfig()
        
        assert cfg.echo is False
        assert cfg.pool_size == 5
    
    def test_main_config(self):
        """Test main Config object."""
        cfg = app_config
        
        assert cfg.chrome is not None
        assert cfg.scrape is not None
        assert cfg.db is not None


class TestConfigFunctions:
    """Test configuration functions."""
    
    def test_get_config(self):
        """Test get_config returns Config."""
        cfg = get_config()
        
        assert isinstance(cfg, Config)
    
    def test_update_config(self):
        """Test update_config."""
        old_wait = app_config.chrome.wait
        
        update_config(chrome={"wait": 15})
        
        assert app_config.chrome.wait == 15
        
        app_config.chrome.wait = old_wait