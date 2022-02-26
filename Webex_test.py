from webexteamssdk import WebexTeamsAPI

api = WebexTeamsAPI(access_token='Y2lzY29zcGFyazovL3VzL0FQUExJQ0FUSU9OL0NkZTQyZDJiZTc4OGZhNzI3ZjI3YTY4OTU2M2UwYmIzYWJiM2E5M2Y1ZWM5ZDFkZDViNGExZDFjZjNiYzc3NGVm')

print(api.people.me())
print(api.rooms.list())
#demo_room = api.rooms.create("Test room")

# Print the room details (formatted JSON)
#print(demo_room)