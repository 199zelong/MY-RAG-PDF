messages=[]

while True:
    user_input = input("输入你想说的话（输入quit退出 )：")
    if user_input == "quit":
        break

    chat_dict= {
         "role": "user",
        "content": user_input
    }
    messages.append(chat_dict)
    print("当前记录：",messages)
print("对话结束，最终发送AI的记录是：",messages)