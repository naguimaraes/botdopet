import asyncio
from asyncio import tasks
from utils.setup import CommandTree, Bot, TOKENS

import commands.help as Help
CommandTree.add_command(Help.Pethelp(Bot), guild=TOKENS.GUILD) # Adiciona os subcomando de ajuda

import commands.key as Key
CommandTree.add_command(Key.Petkey(Bot), guild=TOKENS.GUILD) # Adiciona os subcomando de key

import commands.text_generator as Shks
CommandTree.add_command(Shks.Petshakespear(Bot), guild=TOKENS.GUILD) # Adiciona os subcomando de shakespeare

import commands.offenses as Offenses
CommandTree.add_command(Offenses.Petxingamento(Bot), guild=TOKENS.GUILD) # Adiciona os subcomando de offenses

import commands.praises as Praises
CommandTree.add_command(Praises.Petelogio(Bot), guild=TOKENS.GUILD) # Adiciona os subcomando de elogios

import commands.setenvvar as SEV
CommandTree.add_command(SEV.PetSetEnv(Bot), guild=TOKENS.GUILD) # Adiciona os subcomando de setenvvar

import commands.retro as Retro
CommandTree.add_command(Retro.Petretro(Bot), guild=TOKENS.GUILD) # Adiciona os subcomando de retro

Bot.run(TOKENS.SERVER) # Inicia o bot