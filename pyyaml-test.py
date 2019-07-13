'''import yaml

with open('cortex_config.yaml', 'r') as config:
    stream = config.read()
    print(yaml.dump(yaml.load(stream, Loader=yaml.Loader)))'''


string = '''def bruh():
    print('bruh!!!!!!!')


bruh()'''

exec(string)