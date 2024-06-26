import discord
from discord import app_commands as apc
from discord.ext import tasks
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta, time

from bot import Bot

class Navegador:
    def __init__(self):
        self.DRIVER_PATH = r"utils/chromedriver"
        chromeoptions = webdriver.ChromeOptions()
        chromeoptions.add_argument('--headless')
        chromeoptions.add_argument('--no-sandbox')
        chromeoptions.add_argument('--disable-dev-shm-usage')
        chromeoptions.add_argument('--silent')
        chromeoptions.add_experimental_option('excludeSwitches', ['enable-logging'])

        self.navegador = webdriver.Chrome(executable_path=self.DRIVER_PATH, options=chromeoptions)

@Bot.addCommandGroup
class Petbolsa(apc.Group):
    '''Consulta o pagamento da bolsa'''
    def __init__(self):
        super().__init__() # Inicializa a classe pai
        self.navegador = None
        self.link: str = 'https://www.fnde.gov.br/consulta-publica/pagamento-bolsa-executado/#/app/consultar/0/0'
        self.link_map: dict = {
            'inputs': {
                'cpf': '/html/body/div/section/div/div[2]/div/form/div/div/div/div/input'
            },
            'buttons': {
                'search': '/html/body/div/section/div/div[2]/div/form/div/div/div/div/span[2]',
                'details': '/html/body/div/section/div/div[3]/div[2]/div/table/tbody/tr/td[3]/a'
            },
            'infos': {
                'reference_month': '/html/body/div/section/div/div[2]/div[2]/div/table/tbody/tr[$$PAY_DAY$$]/td[1]',
                'last_payment_day': '/html/body/div/section/div/div[2]/div[2]/div/table/tbody/tr[$$PAY_DAY$$]/td[2]',
                'last_payment_value': '/html/body/div/section/div/div[2]/div[2]/div/table/tbody/tr[$$PAY_DAY$$]/td[4]',
            }
        }

    @apc.command(name="consulta", description="Consulta o pagamento da bolsa") # Adiciona o subcomando consulta
    async def Consulta(self, interaction: discord.Interaction, cpf: str, mostrar: bool = False):
        await interaction.response.defer(thinking=True, ephemeral=True)
        self.navegador = Navegador()

        error = False
        try:
            last_reference_month, last_payment_value = self.search(cpf)
        except: 
            error = True
            last_reference_month, last_payment_value = ('Error', "Erro ao consultar o pagamento da bolsa")

        if not error:
            Bot.Data.Payments['cpf'] = cpf
            Bot.Data.Payments.save()

        em=discord.Embed(title = "**Sua Bolsa**", 
                         description=f"**Valor:** {last_payment_value}\n**Mês de Referencia:** {last_reference_month}",
                         color=0xFFFFFF)
        
        await interaction.followup.send(embed=em, ephemeral=not mostrar)
        self.navegador.navegador.quit()

    def search(self, cpf: str) -> tuple:
        self.navegador.navegador.get(self.link)
        WebDriverWait(self.navegador.navegador, 5).until(EC.presence_of_element_located((By.XPATH, self.link_map['inputs']['cpf']))).send_keys(cpf)
        WebDriverWait(self.navegador.navegador, 5).until(EC.presence_of_element_located((By.XPATH, self.link_map['buttons']['search']))).click()
        WebDriverWait(self.navegador.navegador, 5).until(EC.presence_of_element_located((By.XPATH, self.link_map['buttons']['details']))).click()

        table_line = 2
        while True:
            try:
                WebDriverWait(self.navegador.navegador, 5).until(EC.presence_of_element_located((By.XPATH, self.link_map['infos']['last_payment_day'].replace('$$PAY_DAY$$', str(table_line))))).text
                table_line += 1
            except:
                table_line -= 2
                WebDriverWait(self.navegador.navegador, 5).until(EC.presence_of_element_located((By.XPATH, self.link_map['infos']['last_payment_day'].replace('$$PAY_DAY$$', str(table_line))))).text
                break

        last_reference_month = WebDriverWait(self.navegador.navegador, 5).until(EC.presence_of_element_located((By.XPATH, self.link_map['infos']['reference_month'].replace('$$PAY_DAY$$', str(table_line))))).text
        last_payment_value = WebDriverWait(self.navegador.navegador, 5).until(EC.presence_of_element_located((By.XPATH, self.link_map['infos']['last_payment_value'].replace('$$PAY_DAY$$', str(table_line))))).text
        
        return (last_reference_month, last_payment_value)

    @tasks.loop(count=1)
    async def startTasks(self): # Função para iniciar as tasks
        self.Check.start()   # Inicia a task de aniversario  

    @tasks.loop(time=time(hour=10, minute=10, tzinfo = Bot.TZ))
    async def Check(self):
        channel = Bot.get_channel(Bot.Data.Channels["warning"])
        cpf = Bot.Data.Payments['cpf']
        self.navegador = Navegador()

        try:
            last_reference_month, last_payment_value = self.search(cpf)
        except:
            em=discord.Embed(title = "**Erro ao consultar o pagamento da bolsa**", 
                         description=f"**Atualize o CPF fazendo uma consulta**",
                         color=0xFF0000
                         )
            self.navegador.navegador.quit()

            await channel.send(embed=em)

            return
        
        self.navegador.navegador.quit()

        last_month = datetime.today().replace(day=1) - timedelta(days=1)

        two_months_ago = last_month.replace(day=1) - timedelta(days=1)

        if last_month.strftime("%m/%Y") == last_reference_month and Bot.Data.Payments['date'] != last_reference_month:
            em=discord.Embed(title = "**Bolsa Caiu!**", 
                         description=f"**Valor:** {last_payment_value}\n**Mês de Referencia:** {last_reference_month}",
                         color=0x00FF00
                         )
            Bot.Data.Payments['date'] = last_reference_month
            Bot.Data.Payments.save()

            await channel.send(f'Atenção, <@&{Bot.Data.Roles["petiane"]}>!',embed=em)

        elif two_months_ago.strftime("%m/%Y") == last_reference_month and Bot.Data.Payments['date'] != last_reference_month:
            em=discord.Embed(title = "**Atualização**", 
                         description=f"**O CPF registrado pode estar desafado, por favor, atualize-o fazendo uma consulta**",
                         color=0x00FF00
                         )
            await channel.send(embed=em)
    