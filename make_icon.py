try:
    from PIL import Image, ImageDraw
    
    # 创建一个简单的图标
    img = Image.new('RGB', (256, 256), color='#2196F3')
    draw = ImageDraw.Draw(img)
    
    # 绘制一个播放按钮
    draw.rectangle([64, 64, 192, 192], fill='white')
    draw.polygon([(100, 90), (100, 166), (170, 128)], fill='#2196F3')
    
    # 保存为ICO格式
    img.save('icon.ico', format='ICO', sizes=[(256, 256)])
    print("图标创建成功：icon.ico")
    
except ImportError:
    print("需要安装Pillow库：pip install pillow")
except Exception as e:
    print(f"创建图标失败：{e}")
    print("你可以使用任何在线ICO转换器创建图标")