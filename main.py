import os
command = 'python run.py --model lf --first ./images/first.png --second ./images/second.png --out ./out.png'
result = os.system(command)
print(result)
