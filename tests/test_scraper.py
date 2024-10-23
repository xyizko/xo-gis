import pytest
from unittest.mock import Mock, patch, AsyncMock
from playwright.async_api import Page
from src.scraper import gis
from src.utils import (
    read_repo_names,
    get_user_agent,
    store_results_as_files,
    scrape_github_issues_and_prs
)

# Add pytest-asyncio configuration
pytest_plugins = ('pytest_asyncio',)

@pytest.fixture
def mock_repo_file(tmp_path, monkeypatch):
    repo_file = tmp_path / "repos.txt"
    repo_file.write_text("owner/repo1\nowner/repo2")
    monkeypatch.setattr('src.scraper.repo_file', "config/repos.txt")
    return str(repo_file)

@pytest.fixture
def mock_useragent_file(tmp_path, monkeypatch):
    ua_file = tmp_path / "useragent.txt"
    ua_file.write_text("Mozilla/5.0 Test User Agent")
    monkeypatch.setattr('src.scraper.user_agent_file', "config/useragent.txt")
    return str(ua_file)

@pytest.fixture
def mock_reports_dir(tmp_path):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    return reports_dir

def test_read_repo_names(mock_repo_file):
    repos = read_repo_names(mock_repo_file)
    assert len(repos) == 2
    assert "owner/repo1" in repos
    assert "owner/repo2" in repos

def test_read_empty_repo_file(tmp_path):
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("")
    with pytest.raises(SystemExit):
        read_repo_names(str(empty_file))

def test_get_user_agent(mock_useragent_file):
    ua = get_user_agent(mock_useragent_file)
    assert ua == "Mozilla/5.0 Test User Agent"

def test_get_default_user_agent(tmp_path):
    nonexistent_file = tmp_path / "nonexistent.txt"
    ua = get_user_agent(str(nonexistent_file))
    assert "Mozilla/5.0" in ua
    assert "Chrome" in ua

def test_store_results_as_files(mock_reports_dir, monkeypatch):
    monkeypatch.setattr("src.utils.ensure_reports_folder", lambda: str(mock_reports_dir))
    issues = ["Issue 1", "Issue 2"]
    prs = ["PR 1", "PR 2"]
    store_results_as_files("test-repo", issues, prs)
    
    files = list(mock_reports_dir.glob("*"))
    assert len(files) == 2
    
    json_file = next(mock_reports_dir.glob("*.json"))
    assert json_file.exists()
    
    text_file = next(mock_reports_dir.glob("*.txt"))
    assert text_file.exists()

@pytest.mark.asyncio
async def test_scrape_github_issues_and_prs(mock_reports_dir):
    # Create AsyncMock instead of regular Mock
    mock_page = AsyncMock(spec=Page)
    mock_page.evaluate.return_value = ["Test Issue 1", "Test Issue 2"]
    
    # Make sure these async methods return completed futures
    mock_page.goto = AsyncMock()
    mock_page.wait_for_selector = AsyncMock()
    
    with patch('src.utils.take_screenshot', new_callable=AsyncMock) as mock_screenshot, \
         patch('src.utils.store_results_as_files') as mock_store:
        
        await scrape_github_issues_and_prs(
            "test/repo",
            "https://github.com/test/repo/issues",
            "https://github.com/test/repo/pulls",
            mock_page
        )
        
        assert mock_page.goto.await_count == 2
        assert mock_screenshot.await_count == 2
        assert mock_store.call_count == 1

@pytest.mark.asyncio
async def test_gis_main_function(mock_repo_file, mock_useragent_file, monkeypatch):
    # Mock the console and logging to avoid test output noise
    mock_console = Mock()
    mock_console.line = Mock()
    mock_console.rule = Mock()
    mock_console.print = Mock()
    
    monkeypatch.setattr('src.scraper.console', mock_console)
    monkeypatch.setattr('src.scraper.log', Mock())
    monkeypatch.setattr('src.scraper.list_reports_directory', Mock())
    
    with patch('src.scraper.read_repo_names') as mock_read_repos, \
         patch('src.scraper.get_user_agent') as mock_get_ua, \
         patch('src.scraper.scrape_github_issues_and_prs') as mock_scrape, \
         patch('playwright.async_api.async_playwright') as mock_playwright, \
         patch('src.scraper.track', lambda items, description: items):  # Mock track to just return items
        
        # Setup mock return values
        mock_read_repos.return_value = ["owner/repo1"]
        mock_get_ua.return_value = "Test User Agent"
        mock_scrape.return_value = None
        
        # Create proper async context for playwright
        playwright_context = AsyncMock()
        browser = AsyncMock()
        context = AsyncMock()
        page = AsyncMock()
        
        # Setup the playwright chain
        playwright_context.chromium.launch = AsyncMock(return_value=browser)
        browser.new_context = AsyncMock(return_value=context)
        context.new_page = AsyncMock(return_value=page)
        context.add_init_script = AsyncMock()
        browser.close = AsyncMock()
        
        # Setup the context manager
        mock_playwright.return_value = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = playwright_context
        mock_playwright.return_value.__aexit__.return_value = None
        
        # Call the main function
        await gis()
        
        # Verify the basic mocks were called
        assert mock_playwright.called
        assert mock_read_repos.called
        assert mock_get_ua.called
        
        # Verify the playwright chain
        assert playwright_context.chromium.launch.called
        assert browser.new_context.called
        browser.new_context.assert_called_with(
            user_agent="Test User Agent",
            viewport={"width": 1280, "height": 720}
        )
        
        # Verify init script was added
        assert context.add_init_script.called
        
        # Verify page creation and scraping
        assert context.new_page.called
        assert mock_scrape.called
        mock_scrape.assert_called_with(
            "owner/repo1",
            "https://github.com/owner/repo1/issues",
            "https://github.com/owner/repo1/pulls",
            page
        )
        
        # Verify browser cleanup
        assert browser.close.called