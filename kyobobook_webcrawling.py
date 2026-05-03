"""
교보문고 베스트셀러 크롤러 (Selenium 버전)
동적 페이지 로딩을 위해 Selenium을 사용합니다.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

def crawl_kyobo_bestseller_selenium():
    """Selenium을 사용한 교보문고 베스트셀러 크롤링"""
    url = "https://store.kyobobook.co.kr/bestseller/total/weekly"

    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')  # 새로운 headless 모드
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = None
    books = []

    try:
        # Chrome 드라이버 시작 (자동 설치)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)

        # 페이지 로딩 대기 - 실제 책 컨테이너가 로드될 때까지 기다림
        print("페이지 로딩 중...")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.ml-4.w-full"))
            )
            print("페이지 로딩 완료!")
        except:
            print("페이지 로딩 시간 초과 - 그래도 진행합니다...")
            time.sleep(3)  # 로딩 실패 시 추가 대기

        # 추가 대기 (동적 콘텐츠가 완전히 로드되도록)
        time.sleep(2)

        # 책 정보 추출 - 정확한 선택자 사용
        # ml-4와 w-full 클래스를 가진 div가 각 책의 컨테이너
        book_containers = driver.find_elements(
            By.CSS_SELECTOR,
            "div.ml-4.w-full"
        )

        print(f"발견된 책 컨테이너: {len(book_containers)}개\n")

        if not book_containers:
            print("책 목록을 찾을 수 없습니다.")
            print("페이지 HTML 구조 확인이 필요합니다.")
            print("'page_source.html' 파일을 확인하세요.")
            return []

        for idx, container in enumerate(book_containers, 1):
            try:
                # 책 제목 추출 - prod_link 클래스의 a 태그
                try:
                    title_elem = container.find_element(By.CSS_SELECTOR, "a.prod_link")
                    title = title_elem.text.strip()
                except:
                    print(f"항목 {idx}: 제목을 찾을 수 없습니다.")
                    continue

                if not title:
                    continue

                # 저자 추출 - line-clamp-2 클래스를 가진 div
                author = "저자 정보 없음"
                try:
                    author_div = container.find_element(
                        By.CSS_SELECTOR,
                        "div.line-clamp-2"
                    )
                    author_text = author_div.text.strip()

                    # "·"로 구분된 경우 (저자·역자·출판사 등)
                    if '·' in author_text:
                        parts = author_text.split('·')
                        if len(parts) >= 2:
                            author = parts[0].strip()
                    # "지음"이 포함된 경우
                    elif '지음' in author_text:
                        author = author_text.replace('지음', '').strip()
                    # 그냥 텍스트만 있는 경우
                    elif author_text and len(author_text) < 50:
                        author = author_text
                except:
                    pass  # 저자 정보가 없는 경우 기본값 사용

                books.append({
                    'rank': idx,
                    'title': title,
                    'author': author
                })

            except Exception as e:
                print(f"항목 {idx} 처리 중 오류: {e}")
                continue

        # 결과 출력
        if books:
            print(f"\n교보문고 주간 베스트셀러 (총 {len(books)}권)\n")
            print("=" * 80)
            for book in books:
                print(f"{book['rank']:2d}. {book['title']}")
                print(f"    저자: {book['author']}")
                print("-" * 80)
        else:
            print("책 정보를 추출할 수 없습니다.")

        return books

    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return []

    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    print("교보문고 베스트셀러 크롤링 시작...")
    print("Selenium을 사용하여 페이지를 로딩합니다.\n")

    books = crawl_kyobo_bestseller_selenium()

    # CSV로 저장
    if books:
        with open('kyobo_bestseller.csv', 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['rank', 'title', 'author'])
            writer.writeheader()
            writer.writerows(books)
        print(f"\n결과가 'kyobo_bestseller.csv' 파일로 저장되었습니다.")
