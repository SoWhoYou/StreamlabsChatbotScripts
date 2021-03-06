#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import json
import datetime
import codecs
import clr

#---------------------------------------

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

#---------------------------------------

ScriptName = "Clip Command"
Website = "https://www.sowhoyou.com"
Description = "Create Clips via a Commmand!"
Creator = "SoWhoYou"
Version = "1.0.8.0"

# Special Thanks to: @Ocgineer & @Brain for the assistance, ideas, tips & tricks.

#---------------------------------------

SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")

class Settings(object):
	def __init__(self, settingsfile=None):
		try:
			with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
				self.__dict__ = json.load(f, encoding="utf-8")
		except:
			self.SendToClipToDiscord = False
			self.SendToClipToTwitch = True
			self.Command = "!clip"
			self.DiscordResponse = "{0}"
			self.TwitchResponse = "{0}"
			self.DiscordDMResponse = "{0}"
			self.TwitchWhisperResponse = "{0}"
			self.CommandCost = 0
			self.oAuthToken = "oauth:000000000"
			self.Permission = "Everyone"
			self.PermissionInfo = ""
			self.UserCooldown = 30
			self.GlobalCooldown = 15
			self.ReponseClientIDError = "/me Failed to Clip! ClientID Error! - Generate a New Token in the Script and Make sure to save the Script Settings!"
			self.ReponseApiError = "/me Failed to Clip! API Error! - Generate a New Token in the Script and Make sure to save the Script Settings!"
			self.ReponseNotEnoughPoints = "/me @{0} you only have {1} {2}, you need {3} {2} to use the {4} command!"
			self.ReponseNotEnoughPermissions = "/me @{0} you do not have permission to use the {1} command!"
			self.ReponseGlobalCooldown = "/me @{0} the {1} command is on a global cooldown for another {2} seconds!"
			self.ReponseUserCooldown = "/me @{0} the {1} command is on cooldown for another {2} seconds!"
			self.ReponseNotLive = "/me @{0} the {1} command can only be used while the stream is live!"
		return

	def Reload(self, jsondata):
		self.__dict__ = json.loads(jsondata, encoding="utf-8")
		return

#---------------------------------------

def GetClip(data):
	headers = {
		"Authorization": "Bearer {}".format(ScriptSettings.oAuthToken[6:])
	}
	reply = json.loads(Parent.GetRequest("https://api.twitch.tv/helix/users", headers))
	if reply['status'] == 200:
		jsonToPython = json.loads(reply['response'])
		reply = json.loads(Parent.PostRequest("https://api.twitch.tv/helix/clips?broadcaster_id={0}".format(jsonToPython['data'][0]['id']), headers, {}, True))
		if reply["status"] == 202 :
			resp = json.loads(reply["response"])
			return resp["data"][0]["edit_url"][:-5]
		else:
			return ScriptSettings.ReponseApiError.format(data.User, ScriptSettings.Command)
	else:
		return ScriptSettings.ReponseClientIDError.format(data.User, ScriptSettings.Command)

#---------------------------------------

def GetToken():
	os.startfile("https://api.twitch.tv/kraken/oauth2/authorize?response_type=token&client_id=gag42853avcxx63rhaofcrxr3agoeb"
		+ "&redirect_uri=https://www.sowhoyou.com/oauth/&scope=clips:edit&force_verify=true")
	return

#---------------------------------------

def OpenStream():
	os.startfile("https://www.twitch.tv/sowhoyoudotcom")
	return

#---------------------------------------

def OpenSite():
	os.startfile("https://www.sowhoyou.com/clipcommand/")
	return

#---------------------------------------

def OpenClips():
	os.startfile("https://clips.twitch.tv/my-clips")
	return

#---------------------------------------

def Init():
	global ScriptSettings
	ScriptSettings = Settings(SettingsFile)
	return

#--------------------------------------- SendAllGood

def SendAllGood(data):
	Parent.AddUserCooldown(ScriptName, ScriptSettings.Command, data.User, ScriptSettings.UserCooldown)
	Parent.AddCooldown(ScriptName, ScriptSettings.Command, ScriptSettings.GlobalCooldown)
	holder = GetClip(data) # Prevents duplicates when sending to discord
	if data.IsWhisper(): # Is Whisper
		if data.IsFromTwitch():
			Parent.SendTwitchWhisper(data.User, ScriptSettings.TwitchWhisperResponse.format(holder, data.User))
		else: # Is Discord Response
			if ScriptSettings.SendToClipToDiscord:
				Parent.SendDiscordDM(data.User, ScriptSettings.DiscordDMResponse.format(holder, data.User))
	else: # Not a Whisper
		if data.IsFromTwitch():
			if ScriptSettings.SendToClipToDiscord:
				Parent.SendDiscordMessage(ScriptSettings.DiscordResponse.format(holder, data.User))
			if ScriptSettings.SendToClipToTwitch:
				Parent.SendTwitchMessage(ScriptSettings.TwitchResponse.format(holder, data.User))
		else: # Is Discord Whisper Response
			if ScriptSettings.SendToClipToDiscord:
				Parent.SendDiscordMessage(ScriptSettings.DiscordResponse.format(holder, data.User))
			if ScriptSettings.SendToClipToTwitch:
				Parent.SendTwitchMessage(ScriptSettings.TwitchResponse.format(holder, data.User))

#--------------------------------------- SendNoMoney

def SendNoMoney(data):
	if data.IsWhisper(): # Is Whisper
		if data.IsFromTwitch():
			Parent.SendTwitchWhisper(data.User, ScriptSettings.ReponseNotEnoughPoints.format(
			data.User, Parent.GetPoints(data.User), Parent.GetCurrencyName(), ScriptSettings.CommandCost, ScriptSettings.Command))
		else: # Is Discord Response
			if ScriptSettings.SendToClipToDiscord:
				Parent.SendDiscordDM(data.User, ScriptSettings.ReponseNotEnoughPoints.format(
				data.User, Parent.GetPoints(data.User), Parent.GetCurrencyName(), ScriptSettings.CommandCost, ScriptSettings.Command))
	else: # Not a Whisper Message
		if data.IsFromTwitch():
			Parent.SendTwitchMessage(ScriptSettings.ReponseNotEnoughPoints.format(
			data.User, Parent.GetPoints(data.User), Parent.GetCurrencyName(), ScriptSettings.CommandCost, ScriptSettings.Command))
		else: # Is Discord Response
			if ScriptSettings.SendToClipToDiscord:
				Parent.SendDiscordMessage(ScriptSettings.ReponseNotEnoughPoints.format(
				data.User, Parent.GetPoints(data.User), Parent.GetCurrencyName(), ScriptSettings.CommandCost, ScriptSettings.Command))

#--------------------------------------- SendCooldown

def SendCooldown(data):
	if data.IsWhisper(): # Is Whisper
		if data.IsFromTwitch():
			Parent.SendTwitchWhisper(data.User, ScriptSettings.ReponseUserCooldown.format(
			data.User, ScriptSettings.Command, Parent.GetUserCooldownDuration(ScriptName, ScriptSettings.Command, data.User)))
		else: # Is Discord Response
			if ScriptSettings.SendToClipToDiscord:
				Parent.SendDiscordDM(data.User, ScriptSettings.ReponseUserCooldown.format(
				data.User, ScriptSettings.Command, Parent.GetUserCooldownDuration(ScriptName, ScriptSettings.Command, data.User)))
	else: # Not a Whisper Message
		if data.IsFromTwitch():
			Parent.SendTwitchMessage(ScriptSettings.ReponseUserCooldown.format(
			data.User, ScriptSettings.Command, Parent.GetUserCooldownDuration(ScriptName, ScriptSettings.Command, data.User)))
		else: # Is Discord Response
			if ScriptSettings.SendToClipToDiscord:
				Parent.SendDiscordMessage(ScriptSettings.ReponseUserCooldown.format(
				data.User, ScriptSettings.Command, Parent.GetUserCooldownDuration(ScriptName, ScriptSettings.Command, data.User)))

#---------------------------------------- SendGlobalCooldown

def SendGlobalCooldown(data):
	if data.IsWhisper(): # Is Whisper
		if data.IsFromTwitch():
			Parent.SendTwitchWhisper(data.User, ScriptSettings.ReponseGlobalCooldown.format(
				data.User, ScriptSettings.Command, Parent.GetCooldownDuration(ScriptName, ScriptSettings.Command)))
		else: # Is Discord Response
			if ScriptSettings.SendToClipToDiscord:
				Parent.SendDiscordDM(data.User, ScriptSettings.ReponseGlobalCooldown.format(
				data.User, ScriptSettings.Command, Parent.GetCooldownDuration(ScriptName, ScriptSettings.Command)))
	else: # Not a Whisper Message
		if data.IsFromTwitch():
			Parent.SendTwitchMessage(ScriptSettings.ReponseGlobalCooldown.format(
			data.User, ScriptSettings.Command, Parent.GetCooldownDuration(ScriptName, ScriptSettings.Command)))
		else: # Is Discord Response
			if ScriptSettings.SendToClipToDiscord:
				Parent.SendDiscordMessage(ScriptSettings.ReponseGlobalCooldown.format(
				data.User, ScriptSettings.Command, Parent.GetCooldownDuration(ScriptName, ScriptSettings.Command)))

#---------------------------------------- SendNotEnounghPerms

def SendNotEnounghPerms(data):
	if data.IsWhisper(): # Is Whisper
		if data.IsFromTwitch():
			Parent.SendTwitchWhisper(data.User, ScriptSettings.ReponseNotEnoughPermissions.format(
				data.User, ScriptSettings.Command, ScriptSettings.Permission, ScriptSettings.PermissionInfo))
		else: # Is Discord Response
			if ScriptSettings.SendToClipToDiscord:
				Parent.SendDiscordDM(data.User, ScriptSettings.ReponseNotEnoughPermissions.format(
				data.User, ScriptSettings.Command, ScriptSettings.Permission, ScriptSettings.PermissionInfo))
	else: # Not a Whisper Message
		if data.IsFromTwitch():
			Parent.SendTwitchMessage(ScriptSettings.ReponseNotEnoughPermissions.format(
			data.User, ScriptSettings.Command, ScriptSettings.Permission, ScriptSettings.PermissionInfo))
		else: # Is Discord Response
			if ScriptSettings.SendToClipToDiscord:
				Parent.SendDiscordMessage(ScriptSettings.ReponseNotEnoughPermissions.format(
				data.User, ScriptSettings.Command, ScriptSettings.Permission, ScriptSettings.PermissionInfo))

#---------------------------------------- SendNotLive

def SendNotLive(data):
	if data.IsWhisper(): # Is Whisper
		if data.IsFromTwitch():
			Parent.SendTwitchWhisper(data.User, ScriptSettings.ReponseNotLive.format(data.User, ScriptSettings.Command))
		else: # Is Discord Response
			if ScriptSettings.SendToClipToDiscord:
				Parent.SendDiscordDM(data.User, ScriptSettings.ReponseNotLive.format(data.User, ScriptSettings.Command))
	else: # Not a Whisper Message
		if data.IsFromTwitch():
			Parent.SendTwitchMessage(ScriptSettings.ReponseNotLive.format(data.User, ScriptSettings.Command))
		else: # Is Discord Response
			if ScriptSettings.SendToClipToDiscord:
				Parent.SendDiscordMessage(ScriptSettings.ReponseNotLive.format(data.User, ScriptSettings.Command))

#---------------------------------------- Execute

def Execute(data):
	if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.Command:
		if Parent.IsLive(): # Because how can you make a clip if the stream is offline?
			if Parent.HasPermission(data.User, ScriptSettings.Permission, ScriptSettings.PermissionInfo): # Has Permissions
				if not Parent.IsOnCooldown(ScriptName, ScriptSettings.Command): # Not Global Cooldown
					if not Parent.IsOnUserCooldown(ScriptName, ScriptSettings.Command, data.User): # Not User Cooldown
						if Parent.RemovePoints(data.User, ScriptSettings.CommandCost) or ScriptSettings.CommandCost == 0: # Remove/Check Currency Updated
							SendAllGood(data)
						else: # Not Enought Curreny Response
							SendNoMoney(data)
					else: # User Cooldown Response
						SendUserCooldown(data)
				else: # Global Cooldown Response
					SendGlobalCooldown(data)
			else: # Not Enough Permissions Response
				SendNotEnounghPerms(data)
		else: # Not Live Response
			SendNotLive(data)
	return
 
#---------------------------------------

def Tick():
	return

#---------------------------------------

def ReloadSettings(jsonData):
	ScriptSettings.Reload(jsonData)
	return