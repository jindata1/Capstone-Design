from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from discord.ext import commands
from discord.ui import Select, Button, View
from discord import ButtonStyle, TextStyle, SelectOption
from google.cloud import texttospeech
from gtts import gTTS
from lxml import etree
import discord, random, asyncio,os,time
import requests
from bs4 import BeautifulSoup


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
tree = bot.tree
login_discord = []
login_info = []

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\data4\Desktop\project\inlaid-computer-382511-049fe9d71c76.json"
tts_client = texttospeech.TextToSpeechClient()

language_code = "ko-KR"
voice_name = "ko-KR-Wavenet-A"

def convert_text_to_speech(text):
    input_text = texttospeech.SynthesisInput(text=text)
    voice_params = texttospeech.VoiceSelectionParams(
        language_code=language_code, name=voice_name
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    response = tts_client.synthesize_speech(
        input=input_text, voice=voice_params, audio_config=audio_config
    )
    file_name = "output.mp3"
    with open(file_name, "wb") as out:
        out.write(response.audio_content)
    return file_name

if __name__ == '__main__':
    print(f'[?] 봇을 불러오는 중..')

def Main(code: str, descs: list):
    view = View()  # 컴포넌트 생성
    embed = discord.Embed(title=bot.user.name, description='원하는 버튼을 선택하세요!', color=0x00FFC6)  # 임베드 생성

    for num in range(1, len(descs) + 1):  # 버튼 descs 값만큼 추가
        view.add_item(Button(label=f'{num}', style=ButtonStyle.blurple, custom_id=f'{code}/{num}/0'))

    for num in range(1, len(descs) + 1):  # 필드 descs 값만큼 추가
        embed.add_field(name=f'{num}.', value=descs[num - 1], inline=False)

    return view, embed


async def load(interaction: discord.Interaction, n: str, descs: list):
    view = View()  # 컴포넌트 생성
    embed = discord.Embed(title=bot.user.name, description='원하는 버튼을 선택하세요!', color=0x00FFC6)  # 임베드 생성

    for num in range(1, len(descs) + 1):  # 버튼 1부터 descs 길이 + 1 만큼 추가
        view.add_item(Button(label=f'{num}', style=ButtonStyle.blurple, custom_id=f'main/{n}/{num}'))

    view.add_item(Button(label='뒤로가기', style=ButtonStyle.grey, custom_id=f'back'))  # 뒤로가기 버튼 추가

    for num in range(1, len(descs) + 1):  # 필드 1부터 descs 길이 + 1 만큼 추가
        embed.add_field(name=f'{num}.', value=descs[num - 1], inline=False)

    await interaction.response.edit_message(view=view, embed=embed)



async def load_hoseo_sr(interaction: discord.Interaction, url: str):
    class KeyWord(discord.ui.Modal, title='호서대학교ㅣKeyWord 입력'):
        text = discord.ui.TextInput(
            label='키워드를 입력해 주십시오.',
            placeholder='키워드와 상관없이 최신 글을 보려면 비워두십시오.',
            style=TextStyle.long,
            required=False
        )

        async def on_submit(self, interaction: discord.Interaction):
            embed = discord.Embed(title=bot.user.name, description='⚠️ 정보를 불러오는 중입니다..\n**잠시만 기다려주세요!**',
                                  color=0x00FFC6)

            await interaction.response.edit_message(embed=embed, view=None)

            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--window-size=1024,768')
            options.add_argument('--disable-gpu')

            service = Service(executable_path=ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.implicitly_wait(10)

            try:
                driver.get(url)
                keyword = self.text.value.strip()

                search_url = f"https://www.hoseo.ac.kr/Search/Main.mbz?pageIndex=1&schKeyword={keyword}"
                driver.get(search_url)

                search_list = []
                article_indices = [1, 2]
                li_indices = range(1, 6)
                for article_index in article_indices:
                    for li_index in li_indices:
                        title_elem = driver.find_element(By.XPATH, f'//*[@id="body"]/article[{article_index}]/ul/li[{li_index}]/h4/a')
                        link_elem = driver.find_element(By.XPATH, f'//*[@id="body"]/article[{article_index}]/ul/li[{li_index}]/h4/a')
                        title = title_elem.text.strip()
                        link = link_elem.get_attribute('href').strip()
                        search_list.append(f"Title: {title}\nLink: {link}\n")

                if search_list:
                    result_text = '\n'.join(search_list)
                    embed.title = f'검색 결과: {keyword}'
                    embed.description = result_text
                else:
                    embed.title = '검색 결과 없음'
                    embed.description = f"'{keyword}' 에 대한 검색 결과가 없습니다."

                view = View()  # 컴포넌트 생성
                view.add_item(Button(label='뒤로가기', style=ButtonStyle.grey, custom_id=f'back'))  # 뒤로가기 버튼 추가

                embed = discord.Embed(title=bot.user.name, description='\n'.join(search_list), color=0x00FFC6)
                await interaction.edit_original_response(embed=embed, view=view)


            except Exception as e:
                embed.title = '오류 발생'
                embed.description = f"{type(e).__name__}: {str(e)}"

            finally:
                driver.quit()
                
    await interaction.response.send_modal(KeyWord())

async def load_hoseo(interaction: discord.Interaction, url: str):
    embed = discord.Embed(title=bot.user.name, description='⚠️ 정보를 불러오는 중입니다..\n**잠시만 기다려주세요!**', color=0x00FFC6)
    await interaction.response.edit_message(embed=embed, view=None)

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--window-size=1024,768')
    options.add_argument('--disable-gpu')

    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)

    driver.get(url)
    tbody = '//*[@id="example1"]/tbody/tr'

    def Xpath(key: str):
        return driver.find_element(By.XPATH, key)

    def href(key: str):
        return key.split("'")[1]

    search_list = [
        f'{Xpath(f"{tbody}[{num}]/td[1]").text}ㅣ[{Xpath(f"{tbody}[{num}]/td[2]").text}](http://www.hoseo.ac.kr/Home//BBSView.mbz?action=MAPP_1708240139&schIdx={href(Xpath(f"{tbody}[{num}]/td[2]/a").get_attribute("href"))})\n'
        for num in range(1, 11)]

    view = View()  # 컴포넌트 생성
    view.add_item(Button(label='뒤로가기', style=ButtonStyle.grey, custom_id=f'back'))  # 뒤로가기 버튼 추가

    embed = discord.Embed(title=bot.user.name, description='\n'.join(search_list), color=0x00FFC6)
    await interaction.edit_original_response(embed=embed, view=view)

    driver.close()


async def load_alsw(interaction: discord.Interaction, url: str):
    embed = discord.Embed(title=bot.user.name, description='⚠️ 정보를 불러오는 중입니다..\n**잠시만 기다려주세요!**', color=0x00FFC6)
    await interaction.response.edit_message(embed=embed, view=None)

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--window-size=1024,768')
    options.add_argument('--disable-gpu')

    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)

    driver.get(url)
    tbody = '//*[@id="wrap"]/section[3]/div/div[3]/ul/li'

    def Xpath(key: str):
        return driver.find_element(By.XPATH, key)

    search_list = [
        f'{Xpath(f"{tbody}[{num}]/span").text}ㅣ[{Xpath(f"{tbody}[{num}]/div[1]/a").text}]({Xpath(f"{tbody}[{num}]/div[1]/a").get_attribute("href")})\n'
        for num in range(1, 11)]

    view = View()  # 컴포넌트 생성
    view.add_item(Button(label='뒤로가기', style=ButtonStyle.grey, custom_id=f'back'))  # 뒤로가기 버튼 추가

    embed = discord.Embed(title=bot.user.name, description='\n'.join(search_list), color=0x00FFC6)
    await interaction.edit_original_response(embed=embed, view=view)

    driver.close()


async def load_fotal(interaction: discord.Interaction, url: str, key_list: list):
    if interaction.user.id in login_discord:
        embed = discord.Embed(title=bot.user.name, description='⚠️ 정보를 불러오는 중입니다..\n**잠시만 기다려주세요!**', color=0x00FFC6)
        await interaction.response.edit_message(embed=embed, view=None)

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--window-size=1024,768')
        options.add_argument('--disable-gpu')

        service = Service(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(10)

        driver.get(url)

        driver.find_element(By.XPATH, '//*[@id="user_id"]').send_keys(login_info[login_discord.index(interaction.user.id)].split('/')[0])
        driver.find_element(By.XPATH, '//*[@id="user_password"]').send_keys(login_info[login_discord.index(interaction.user.id)].split('/')[1])
        driver.find_element(By.XPATH, '//*[@id="loginBtn"]').click()

        embed = discord.Embed(title=bot.user.name, description='학생 조회 결과입니다.', color=0x00FFC6)

        if '학사일정' in key_list:
            field_name = '학사일정'
            field_value = driver.find_element(By.XPATH, '//*[@id="schedulelist"]').text
            embed.add_field(name=field_name, value=f"```\n{field_value}```", inline=False)

        if '출결조회' in key_list:
            field_name = '강의시간표'
            field_value = driver.find_element(By.XPATH, '//*[@id="AjaxPtlBodyeXPortal_Sch009Portlet_v0jwin_12_"]/div[2]').text
            embed.add_field(name=field_name, value=f"```\n{field_value}```", inline=False)

        if '이수내역' in key_list:
            field_name = '출결조회'
            field_value = driver.find_element(By.XPATH, f'//*[@id="AjaxPtlBodyeXPortal_Sch010Portlet_v0jwin_10_"]/div').text
            embed.add_field(name=field_name, value=f"```\n{field_value}```", inline=False)

        if '강의시간표' in key_list:
            field_name = '이수내역 확인'
            field_value = driver.find_element(By.XPATH, '//*[@id="AjaxPtlBodyeXPortal_Sch006Portlet_v0jwin_2_"]').text
            embed.add_field(name=field_name, value=f"```\n{field_value}```", inline=False)

        if '마일리지 현황' in key_list:
            field_name = '마일리지 현황'
            field_value = driver.find_element(By.XPATH, '//*[@id="Cds008Portlet!v0jwin|7"]/div/div[2]/div').text
            embed.add_field(name=field_name, value=f"```\n{field_value}```", inline=False)

        if len(embed.fields) > 0:
            field_text = ''
            for field in embed.fields:
                field_text += f"{field.name}: {field.value}\n"
            file_name = convert_text_to_speech(field_text)

            if interaction.user.voice:
                voice_channel = interaction.user.voice.channel
                vc = await voice_channel.connect()
                vc.play(discord.FFmpegPCMAudio(file_name))

                while vc.is_playing():
                    await asyncio.sleep(1)

                await vc.disconnect()
                os.remove(file_name)
            else:
                await interaction.response.edit_message(content="You are not connected to a voice channel.")
        else:
            await interaction.response.edit_message(content="No matching key found.")


        view = View()  # 컴포넌트 생성
        view.add_item(Button(label='뒤로가기', style=ButtonStyle.grey, custom_id=f'back'))  # 뒤로가기 버튼 추가
        await interaction.edit_original_response(embed=embed, view=view)

        driver.close()

    else:
        view = View()
        view.add_item(Button(label='로그인 정보 추가', emoji='🔑', style=ButtonStyle.blurple, custom_id='login'))
        embed = discord.Embed(title=bot.user.name, description='⚠ **로그인 정보가 만료되었습니다!**\n`아래 버튼을 눌러 로그인을 해주세요.`', color=0x00FFC6)
        await interaction.response.send_message(view=view, embed=embed, ephemeral=True)

async def load_lms(interaction: discord.Interaction, url: str, selected_options: list):
    if interaction.user.id in login_discord:
        embed = discord.Embed(title=bot.user.name, description='⚠️ 정보를 불러오는 중입니다..\n**잠시만 기다려주세요!**', color=0x00FFC6)
        await interaction.response.edit_message(embed=embed, view=None)

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--window-size=1024,768')
        options.add_argument('--disable-gpu')

        service = Service(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(10)

        driver.get(url)

        driver.find_element(By.XPATH, '//*[@id="input-username"]').send_keys(
            login_info[login_discord.index(interaction.user.id)].split('/')[0])
        driver.find_element(By.XPATH, '//*[@id="input-password"]').send_keys(
            login_info[login_discord.index(interaction.user.id)].split('/')[1])
        driver.find_element(By.XPATH, '//*[@id="region-main"]/div/div/div[1]/div[1]/div[2]/div/form/div[1]/div[2]/button').click()

        async def show_course_list():
            driver.get('https://learn.hoseo.ac.kr/local/ubion/user/index.php')
            course_links = driver.find_elements(By.XPATH, '//*[@id="region-main"]/div/div/div[2]/div/table/tbody/tr/td[2]/div/a')

            if course_links:
                embed = discord.Embed(title=bot.user.name, description='수강강좌 목록', color=0x00FFC6)
                for i, link in enumerate(course_links):
                    course_id = link.get_attribute('href').split('=')[-1]  # 링크 URL에서 강좌 ID 추출
                    course_name = link.text
                    embed.add_field(name=f'{i+1} {course_name}', value='\u200b', inline=False)

                view = View()  # 컴포넌트 생성
                view.add_item(Button(label='뒤로가기', style=ButtonStyle.grey, custom_id=f'back'))  # 뒤로가기 버튼 추가

                await interaction.followup.send(embed=embed, view=view)

                def check(m):
                    return m.author == interaction.user and m.channel == interaction.channel

                await interaction.followup.send("번호를 입력하세요: ")
                response = await bot.wait_for('message', check=check)
                selected_course_number = int(response.content)

                if 1 <= selected_course_number <= len(course_links):
                    selected_link = course_links[selected_course_number - 1]
                    selected_course_id = selected_link.get_attribute('href').split('=')[-1]  # 링크 URL에서 강좌 ID 추출

                    # 온라인출석부 또는 과제제출 선택 안내
                    selection_embed = discord.Embed(title=bot.user.name, description='온라인출석부 또는 공지사항을 선택해주세요.', color=0x00FFC6)
                    selection_embed.add_field(name='1. 온라인출석부', value='\u200b', inline=False)
                    selection_embed.add_field(name='2. 과제제출', value='\u200b', inline=False)
                    await interaction.followup.send(embed=selection_embed)
                    await interaction.followup.send("번호를 입력하세요: ")

                    selection_response = await bot.wait_for('message', check=check)
                    selected_option = int(selection_response.content)

                    if selected_option == 1:
                        url = f'https://learn.hoseo.ac.kr/report/ubcompletion/user_progress_a.php?id={selected_course_id}'

                        driver.get(url)
                        table_rows = driver.find_elements(By.XPATH, '//*[@id="ubcompletion-progress-wrapper"]/div[2]/table/tbody/tr')
                        x_positions = []

                        for row in table_rows:
                            cells = row.find_elements(By.XPATH, './td')
                            if len(cells) >= 5 and cells[4].text == 'O':
                                name = cells[1].text
                                attendance = cells[4].text
                                x_positions.append((name, attendance))

                        embed = discord.Embed(title=bot.user.name, description='온라인출석부', color=0x00FFC6)

                        if x_positions:
                            for name, attendance in x_positions:
                                embed.add_field(name=name, value=attendance, inline=False)
                        else:
                            embed.add_field(name='알림', value='테이블에서 "O"를 찾을 수 없습니다.', inline=False)

                        view = View()  # 컴포넌트 생성
                        view.add_item(Button(label='뒤로가기', style=ButtonStyle.grey, custom_id=f'back'))  # 뒤로가기 버튼 추가

                        await interaction.followup.send(embed=embed, view=view)

                    if selected_option == 2:
                        url = f'https://learn.hoseo.ac.kr/mod/assign/index.php?id={selected_course_id}'
                        driver.get(url)

                        table_rows = driver.find_elements(By.XPATH, '//*[@id="region-main"]/div/table/tbody/tr')
                        table_data = []

                        for row in table_rows:
                            cells = row.find_elements(By.XPATH, './td')
                            row_data = [cell.text for cell in cells]
                            table_data.append(row_data)

                        embed = discord.Embed(title=bot.user.name, description='온라인출석부', color=0x00FFC6)

                        if table_data:
                            for i, row_data in enumerate(table_data, 1):
                                row_info = ', '.join(row_data)
                                embed.add_field(name=f'\u200b', value=row_info, inline=False)
                        else:
                            embed.add_field(name='알림', value='테이블에서 정보를 찾을 수 없습니다.', inline=False)

                        view = View()  # 컴포넌트 생성
                        view.add_item(Button(label='뒤로가기', style=ButtonStyle.grey, custom_id=f'back'))  # 뒤로가기 버튼 추가

                        await interaction.followup.send(embed=embed, view=view)


                    else:
                        response_text = '잘못된 선택지입니다.'
                        await interaction.followup.send(response_text)

                else:
                    response_text = '잘못된 과목 번호입니다.'
                    await interaction.followup.send(response_text)

            else:
                response_text = '수강강좌가 없습니다.'
                await interaction.followup.send(response_text)

        async def show_all_notifications():
            driver.get('https://learn.hoseo.ac.kr/local/ubnotification/')
            notifications = driver.find_elements(By.XPATH, '//*[@id="page-content"]/div[2]/div/div/div[2]')

            if notifications:
                embed = discord.Embed(title=bot.user.name, description='전체알림', color=0x00FFC6)
                for i, notification in enumerate(notifications):
                    embed.add_field(name=f'Notification {i+1}', value=notification.text, inline=False)
            else:
                embed = discord.Embed(title=bot.user.name, description='전체알림이 없습니다.', color=0x00FFC6)

            view = View()  # 컴포넌트 생성
            view.add_item(Button(label='뒤로가기', style=ButtonStyle.grey, custom_id=f'back'))  # 뒤로가기 버튼 추가
            await interaction.edit_original_response(embed=embed, view=view)

        if '온라인출석부' in selected_options:
            await show_course_list()

        if '전체알림' in selected_options:
            await show_all_notifications()

        driver.close()



@bot.event
async def on_ready():
    print(f'[!] 로그인 성공, {bot.user.name}.')

@bot.event
async def on_interaction(interaction: discord.Interaction):
    custom_id = interaction.data['custom_id']  # 상호작용한 버튼의 custom_id 값

    if custom_id.startswith('main'):
        number1 = int(custom_id.split('/')[1])
        number2 = int(custom_id.split('/')[2])

        if number1 == 1 and number2 == 0:  # 학교 공지사항
            await load(interaction, '1', ['공지사항', '학사공지', '사회봉사','검색'])

        elif number1 == 1 and number2 == 1:  # 공지사항
            await load_hoseo(interaction, 'http://www.hoseo.ac.kr/Home//BBSList.mbz?action=MAPP_1708240139&schIdx=0&schCategorycode=CTG_17082400011&schKeytype=subject&schKeyword=&pageIndex=1')

        elif number1 == 1 and number2 == 2:  # 학사공지
            await load_hoseo(interaction, 'http://www.hoseo.ac.kr/Home//BBSList.mbz?action=MAPP_1708240139&schIdx=0&schCategorycode=CTG_17082400012&schKeytype=subject&schKeyword=&pageIndex=1')

        elif number1 == 1 and number2 == 3:  # 사회봉사
            await load_hoseo(interaction, 'http://www.hoseo.ac.kr/Home//BBSList.mbz?action=MAPP_1708240139&schIdx=0&schCategorycode=CTG_17082400014&schKeytype=subject&schKeyword=&pageIndex=1')

        elif number1 == 1 and number2 == 4:  # 검색
            await load_hoseo_sr(interaction, 'https://www.hoseo.ac.kr/')

        elif number1 == 2 and number2 == 0:  # AISW 중심 사업단 홈페이지
            await load(interaction, '2', ['서식자료실', '공지사항 조회'])

        elif number1 == 2 and number2 == 1:  # 서식자료실
            await load_alsw(interaction, 'https://aisw.hoseo.ac.kr/board/form')

        elif number1 == 2 and number2 == 2:  # 공지사항 조회
            await load_alsw(interaction, 'https://aisw.hoseo.ac.kr/board/notice')

        elif number1 == 3 and number2 == 0:  # 호서대학교 포털사이트
            if interaction.user.id not in login_discord:
                view = View()
                view.add_item(Button(label='로그인 정보 추가', emoji='🔑', style=ButtonStyle.blurple, custom_id='login'))
                embed = discord.Embed(title=bot.user.name, description='⚠ **로그인 정보가 만료되었습니다!**\n`아래 버튼을 눌러 로그인을 해주세요.`',
                                      color=0x00FFC6)
                await interaction.response.send_message(view=view, embed=embed, ephemeral=True)

            random_key = random.randint(0, 0xFFFFFF)

            view = View()
            view.add_item(Select(
                placeholder='여기를 클릭하여 정보들을 선택하세요.',
                min_values=1,
                max_values=5,
                custom_id=f'포털사이트/{random_key}',
                options=[
                    SelectOption(label='학사일정', description='호서대학교의 연간 학사일정', emoji='📄'),
                    SelectOption(label='강의시간표', description='오늘의 강의시간표', emoji='📜'),
                    SelectOption(label='출결조회', description='학생 개인의 출결조회', emoji='📑'),
                    SelectOption(label='이수내역', description='학생 개인의 이수내역', emoji='💻'),
                    SelectOption(label='마일리지 현황', description='학생 개인의 마일리지', emoji='🪙'),
                ]
            ))
            embed = discord.Embed(title=bot.user.name, description='포털사이트에서 조회할 정보들을 선택해주세요.', color=0x00FFC6)
            await interaction.response.send_message(embed=embed, view=view)

            try:
                def check(m):
                    return m.data['custom_id'] == f'포털사이트/{random_key}' and interaction.user == m.user

                interaction = await bot.wait_for('interaction', check=check, timeout=30)
                await load_fotal(interaction, 'https://sso.hoseo.edu/svc/tk/Auth.do?id=NEW_PORTAL&ac=Y&RelayState=%%2Findex.jsp&ifa=N&', interaction.data['values'])

            except asyncio.exceptions.TimeoutError:
                await interaction.delete_original_response()

        elif number1 == 4 and number2 == 0:  # lms 수강강좌 조회

            random_key = random.randint(0, 0xFFFFFF)

            view = View()
            view.add_item(Select(
                placeholder='여기를 클릭하여 정보들을 선택하세요.',
                min_values=1,
                max_values=2,
                custom_id=f'lms/{random_key}',
                options=[
                    SelectOption(label='온라인출석부', description='수강강좌 확인하기', emoji='📕'),
                    SelectOption(label='전체알림', description='알림 확인하기', emoji='🔔'),
                ]
            ))
            embed = discord.Embed(title=bot.user.name, description='lms에서 조회할 정보들을 선택해주세요.', color=0x00FFC6)
            await interaction.response.send_message(embed=embed, view=view)

            try:
                def check(m):
                    return m.data['custom_id'] == f'lms/{random_key}' and interaction.user == m.user

                interaction = await bot.wait_for('interaction', check=check, timeout=30)
                await load_lms(interaction, 'https://learn.hoseo.ac.kr/', interaction.data['values'])
            
            except asyncio.exceptions.TimeoutError:
                await interaction.delete_original_response()
        
    if custom_id == 'back':
        main = Main('main', ['학교 공지사항', 'AISW 중심 사업단 홈페이지', '호서대 포털사이트','lms'])

        await interaction.response.edit_message(view=main[0], embed=main[1], content=None)

    if custom_id == 'login':
        if interaction.user.id in login_discord:
            view = View()
            view.add_item(Button(label='로그인 정보 삭제', emoji='🗑', style=ButtonStyle.red, custom_id='logout'))
            embed = discord.Embed(title=bot.user.name, description='⚠ **이미 로그인 되어있습니다!**\n`삭제를 원하신다면 아래 버튼을 눌러주세요.`', color=0x00FFC6)
            await interaction.response.send_message(view=view, embed=embed, ephemeral=True)

        else:
            class Modal(discord.ui.Modal, title=f"{bot.user.name} / 로그인 정보 추가"):

                ID = discord.ui.TextInput(
                    style=TextStyle.short,
                    label="포털 아이디를 입력해주세요.",
                    required=True,
                    min_length=1,
                    max_length=20
                )

                PW = discord.ui.TextInput(
                    style=TextStyle.short,
                    label="포털 비밀번호를 입력해주세요.",
                    required=True,
                    min_length=1,
                    max_length=20
                )

                async def on_submit(self, interaction: discord.Interaction):
                    embed = discord.Embed(title=bot.user.name, description='⚠️ 정보를 처리하는 중입니다..\n**잠시만 기다려주세요!**', color=0x00FFC6)
                    await interaction.response.edit_message(embed=embed, view=None)

                    options = webdriver.ChromeOptions()
                    options.add_argument('--headless')
                    options.add_argument('--window-size=1024,768')
                    options.add_argument('--disable-gpu')

                    service = Service(executable_path=ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=options)
                    driver.implicitly_wait(10)

                    driver.get('https://sso.hoseo.edu/svc/tk/Auth.do?id=NEW_PORTAL&ac=Y&RelayState=%%2Findex.jsp&ifa=N&')

                    driver.find_element(By.XPATH, '//*[@id="user_id"]').send_keys(self.ID.value)
                    driver.find_element(By.XPATH, '//*[@id="user_password"]').send_keys(self.PW.value)
                    driver.find_element(By.XPATH, '//*[@id="loginBtn"]').click()

                    if driver.current_url == 'https://learn.hoseo.ac.kr/login.php?errorcode=3':
                        embed = discord.Embed(title=bot.user.name, description='⚠ **로그인 정보가 올바르지 않습니다!**', color=0x00FFC6)
                        await interaction.edit_original_response(embed=embed)

                    else:
                        login_discord.append(interaction.user.id)
                        login_info.append(f'{self.ID.value}/{self.PW.value}')
                        embed = discord.Embed(title=bot.user.name, description='✅ **로그인 정보를 저장했습니다!**', color=0x00FFC6)
                        await interaction.edit_original_response(embed=embed)

                    driver.close()

            await interaction.response.send_modal(Modal())

    if custom_id == 'logout':
        if interaction.user.id in login_discord:
            del login_info[login_discord.index(interaction.user.id)]
            del login_discord[login_discord.index(interaction.user.id)]

            embed = discord.Embed(title=bot.user.name, description='✅ **로그인 정보 삭제가 완료되었습니다!**', color=0x00FFC6)
            await interaction.response.send_message(view=view, embed=embed, ephemeral=True)

        else:
            embed = discord.Embed(title=bot.user.name, description='❌ **로그인 정보가 존재하지 않습니다.**', color=0x00FFC6)
            await interaction.response.send_message(view=view, embed=embed, ephemeral=True)


@bot.command(name="목록")  # !목록
async def command_list(ctx):
    main = Main('main', ['학교 공지사항', 'AISW 중심 사업단 홈페이지', '호서대 포털사이트','lms'])

    await ctx.send(view=main[0], embed=main[1], reference=ctx.message)

bot.run('OTg5NDQ3Nzc5MDkwODU4MDY1.GL8a2q.XrxQdd3IKDEycHrT7cphmS8beLTm9AVxWNJoM8')
