local run = game:GetService("RunService")
local RunService = game:GetService("RunService")

-- //  Settings
local password = script.password.Value
local priv = game.PrivateServerId ~= "" and game.PrivateServerOwnerId ~= 0
local channel = script.channel.Value


local id = 0


if priv then
	id = game.PrivateServerId
else
	id = game.JobId
	if tostring(id) == "" then
		id = 0
	end
end
local http = game:GetService("HttpService")
local url = script.url.Value
local commands = {}
local org = {
	["password"] = password,
	['server'] = tostring(id),
	['queue'] = {}
}
local queue = {
	["password"] = password,
	['server'] = tostring(id),
	['queue'] = {}
}
game.ReplicatedStorage.send.Event:Connect(function(msg)
	table.insert(queue['queue'], {['message'] = msg, ['channel'] = channel})
end)

function post()
	local counter = 0
	local desiredInterval = 20
	RunService.Heartbeat:Connect(function(step)
		counter = counter + step 
		if counter >= desiredInterval then
			counter = counter - desiredInterval
			local resp = http:PostAsync(url,http:JSONEncode(queue), Enum.HttpContentType.ApplicationJson)
			queue = org
			local json = http:JSONDecode(resp)
			local use = true
			if json['auth'] == 'allow' then
				for i, v in pairs(json['queue']) do
					if type(v) == "table" then
						for x, c in pairs(v) do
							process_command(x,c)
						end
					end
				end
			end
		end
	end)
end

function start()
	if not run:IsStudio() then
		local data = {
			["password"] = password,
			["start"] = tostring(id),
			['server'] = tostring(id)
		}
		print('Sending POST request')
		local resp = http:PostAsync(url,http:JSONEncode(data), Enum.HttpContentType.ApplicationJson)
		local json = http:JSONDecode(resp)
		if json['auth'] == 'allow' then
			for i, v in pairs(json['queue']) do
				if type(v) == "table" then
					for x, c in pairs(v) do
						process_command(x,c)
					end
				end
			end
			post()
		end
	end
end

commands.message = function(args)
-- Send an announcement message e.g. game.ReplicatedStorage.message:FireAllClients(args)
end

function process_command(item, value)
	local command = string.lower(item)
	if commands[command] then
		commands[command](value)
	end
end

start()

game:BindToClose(function()
	local data = {
		["password"] = password,
		["stop"] = tostring(id),
		['server'] = tostring(id)
		
	}
	print('Sending POST request')
	local resp = http:PostAsync(url,http:JSONEncode(data), Enum.HttpContentType.ApplicationJson)
	local json = http:JSONDecode(resp)
	if json['auth'] == 'allow' then
		print('Server stopped')
	else
		print('Unauthorized')
	end
end)
