content=open('voice_commander.py', encoding='utf-8').read()
idx=content.find('elif action_type == "monitoring_liability":')
print(content[idx:idx+1000])
