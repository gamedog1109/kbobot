from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def debug_kbo_page():
    with sync_playwright() as p:
        print("🔍 Playwright 실행 시작")
        browser = p.chromium.launch(headless=False)  # 창 직접 띄워서 확인
        page = browser.new_page()

        url = "https://www.koreabaseball.com/Schedule/GameCenter/Main.aspx"
        page.goto(url)
        print("⏳ 페이지 로딩 중...")

        try:
            page.wait_for_selector("li.game-cont", timeout=10000)
            print("✅ li.game-cont 요소 감지됨")
        except:
            print("❌ li.game-cont 요소를 찾지 못했습니다 (10초 경과)")

        html = page.content()
        print("\n📄 HTML 일부 출력 (앞부분 2000자):\n")
        print(html[:2000])

        soup = BeautifulSoup(html, "html.parser")
        games = soup.select("li.game-cont")
        print(f"\n🎯 감지된 경기 개수: {len(games)}")

        for i, game in enumerate(games[:3], start=1):
            status = game.select_one("p.staus")
            away = game.select_one("div.team.away img")
            home = game.select_one("div.team.home img")
            score_away = game.select_one("div.team.away .score")
            score_home = game.select_one("div.team.home .score")

            print(f"\n--- 경기 {i} ---")
            print(f"상태: {status.text.strip() if status else '없음'}")
            print(f"원정팀: {away['alt'] if away else '없음'} / 점수: {score_away.text.strip() if score_away else '없음'}")
            print(f"홈팀: {home['alt'] if home else '없음'} / 점수: {score_home.text.strip() if score_home else '없음'}")

        browser.close()

if __name__ == "__main__":
    debug_kbo_page()
