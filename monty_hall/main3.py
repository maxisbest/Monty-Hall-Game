
import pygame, sys
from pygame.locals import *
import random
import time
from time import sleep
from datetime import datetime
from os import path

pygame.init()
pygame.mixer.init()

# 窗口设置
display_width = 1200 # 800
display_height = 900 # 1300

# 文件夹路径初始化
media = path.join(path.dirname(__file__), 'media')

# 完全重新设计的布局参数
TOP_SECTION_HEIGHT = 200    # 顶部说明区域高度
DOOR_SECTION_Y = 220        # 门区域起始Y坐标
DOOR_SECTION_HEIGHT = 300   # 门区域高度
BOTTOM_SECTION_Y = 540 + 200      # 底部区域起始Y坐标

# 左右分栏
LEFT_COLUMN_X = 50
LEFT_COLUMN_WIDTH = 600
RIGHT_COLUMN_X = 700
RIGHT_COLUMN_WIDTH = 650

# 门的位置 - 确保在中央区域
DOOR_AREA_X = 200
DOOR_SPACING = 200
DOOR1_X = DOOR_AREA_X
DOOR2_X = DOOR_AREA_X + DOOR_SPACING
DOOR3_X = DOOR_AREA_X + DOOR_SPACING * 2
DOORS_Y = DOOR_SECTION_Y + 20

# 统一的行间距
LINE_HEIGHT = 30
SECTION_GAP = 15

clock = pygame.time.Clock()
random.seed(int(datetime.now().timestamp()))

pygame.font.init()

gameExit = False
gameOver = False
FPS = 100
sleepTime = 0
numOfWins = numOfGames = numOfLosses = 0
numOfSwaps = 0
numOfWinsBySwap = 0
door_num = 0

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIME = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (100, 150, 255)
GREEN = (0, 200, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PURPLE = (255, 0, 255)

# 加载图片和声音
try:
    door1Image = pygame.image.load(path.join(media + '/door1.jpg'))
    door2Image = pygame.image.load(path.join(media + '/door2.jpg'))
    door3Image = pygame.image.load(path.join(media + '/door3.jpg'))
    openGoatImage = pygame.image.load(path.join(media + '/opengoat.jpg'))
    openCarImage = pygame.image.load(path.join(media + '/opencar.jpg'))
    backgroundImage = pygame.image.load(path.join(media + '/background.jpg'))
    congoImage = pygame.image.load(path.join(media + '/congo.gif'))
    oopsImage = pygame.image.load(path.join(media + '/oops.png'))
    gameSound = path.join(media + '/gameSound.mp3')
    gameIcon = pygame.image.load(path.join(media + '/gameIcon.jpeg'))
    startImage = pygame.image.load(path.join(media + '/startImage.jpeg'))
    promptImage = pygame.image.load(path.join(media + '/prompt.png'))
    chosenImage = pygame.image.load(path.join(media + '/chosen.jpg'))
except pygame.error as e:
    print(f"无法加载图片文件: {e}")
    print("请确保 media 文件夹中包含所有必需的图片文件")
    sys.exit()

gameDisplay = pygame.display.set_mode((display_width, display_height), RESIZABLE)
screen = gameDisplay
pygame.display.set_caption('蒙提霍尔问题')
pygame.display.set_icon(gameIcon)

backgroundRect = backgroundImage.get_rect()
startImageRect = startImage.get_rect()

doorImageList = [door1Image, door2Image, door3Image]
coordinates = [[DOOR1_X, DOORS_Y], [DOOR2_X, DOORS_Y], [DOOR3_X, DOORS_Y]]
possibleImageList = [openCarImage, openGoatImage]
imageList = [0, 1, 2]

class FontManager:
    """字体管理器"""
    
    def __init__(self):
        self.fonts = {}
        self.load_fonts()
    
    def load_fonts(self):
        chinese_fonts = [
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/Hiragino Sans GB.ttc',
            '/System/Library/Fonts/STHeiti Light.ttc',
            '/System/Library/Fonts/Arial Unicode.ttf',
            'fonts/NotoSansCJK-Regular.ttc',
            'fonts/SimHei.ttf'
        ]
        
        font_sizes = [16, 18, 20, 22, 24, 28, 32, 40, 50]
        
        for size in font_sizes:
            font = None
            for font_path in chinese_fonts:
                if path.exists(font_path):
                    try:
                        font = pygame.font.Font(font_path, size)
                        break
                    except:
                        continue
            
            if font is None:
                try:
                    font = pygame.font.Font(None, size)
                except:
                    font = pygame.font.get_default_font()
                    font = pygame.font.Font(font, size)
            
            self.fonts[size] = font
    
    def get_font(self, size):
        if size not in self.fonts:
            try:
                self.fonts[size] = pygame.font.Font(None, size)
            except:
                self.fonts[size] = self.fonts[20]
        return self.fonts[size]

font_manager = FontManager()

def displayImage(x, y, currentImage):
    """显示图片"""
    gameDisplay.blit(currentImage, (x, y))

def showMessage(message, x, y, font_size=20, color=WHITE):
    """显示消息"""
    font = font_manager.get_font(font_size)
    text_surface = font.render(message, True, color)
    gameDisplay.blit(text_surface, (x, y))
    return text_surface.get_height()

def draw_panel_background(x, y, width, height, alpha=120):
    """绘制半透明背景面板"""
    panel = pygame.Surface((width, height))
    panel.set_alpha(alpha)
    panel.fill((20, 20, 20))
    gameDisplay.blit(panel, (x, y))

def clear_area(x, y, width, height):
    """清除指定区域"""
    clear_surface = pygame.Surface((width, height))
    clear_surface.fill(BLACK)
    gameDisplay.blit(clear_surface, (x, y))

def draw_section_dividers():
    """绘制区域分割线（调试用）"""
    # 顶部区域底线
    pygame.draw.line(gameDisplay, (50, 50, 50), (0, TOP_SECTION_HEIGHT), (display_width, TOP_SECTION_HEIGHT), 2)
    # 门区域底线
    pygame.draw.line(gameDisplay, (50, 50, 50), (0, DOOR_SECTION_Y + DOOR_SECTION_HEIGHT), 
                    (display_width, DOOR_SECTION_Y + DOOR_SECTION_HEIGHT), 2)

def setImagesRandomly():
    """随机设置门后的物品"""
    randomList = random.sample(range(0, 3), 3)
    imageList[randomList[0]] = possibleImageList[1]  # 山羊
    imageList[randomList[1]] = possibleImageList[0]  # 汽车
    imageList[randomList[2]] = possibleImageList[1]  # 山羊

def displayStartImages():
    """显示初始的门"""
    for i in range(3):
        displayImage(coordinates[i][0], coordinates[i][1], doorImageList[i])

def revealImage(doorNumber):
    """揭示指定门后的物品"""
    displayImage(coordinates[doorNumber][0], coordinates[doorNumber][1], imageList[doorNumber])

def displayGoat(keyValue):
    """显示一只山羊"""
    available_doors = []
    for i in range(3):
        if i != keyValue and imageList[i] != openCarImage:
            available_doors.append(i)
    
    if available_doors:
        door_to_reveal = random.choice(available_doors)
        revealImage(door_to_reveal)
        return door_to_reveal
    return None

def validate(doorNumber):
    """验证玩家的选择并更新统计"""
    global numOfWins, numOfLosses, numOfGames
    
    # 在底部区域显示结果
    result_y = BOTTOM_SECTION_Y
    clear_area(LEFT_COLUMN_X, result_y, LEFT_COLUMN_WIDTH, 100)
    
    if imageList[doorNumber] == openCarImage:
        numOfWins += 1
        numOfGames += 1
        result_x = LEFT_COLUMN_X + 300
        showMessage('🎉 恭喜你！你赢了！', result_x, result_y, font_size=28, color=GREEN)
        showMessage('按 Q 键继续游戏', result_x, result_y + 35, font_size=20, color=YELLOW)
        return 1
    else:
        numOfLosses += 1
        numOfGames += 1
        result_x = LEFT_COLUMN_X + 300
        showMessage('😢 很遗憾，你输了！', result_x, result_y, font_size=28, color=RED)
        showMessage('按 Q 键继续游戏', result_x, result_y + 35, font_size=20, color=YELLOW)
        return 0

def show_title():
    """显示标题"""
    title_y = 20
    showMessage('Monty Hall Problem', display_width // 2 - 200, title_y, font_size=30, color=LIME)

def show_game_rules():
    """显示游戏规则 - 在顶部左侧"""
    rules_y = 70
    draw_panel_background(LEFT_COLUMN_X - 10, rules_y - 10, LEFT_COLUMN_WIDTH - 200, 120)
    
    current_y = rules_y
    showMessage('🎯 游戏规则:', LEFT_COLUMN_X, current_y, font_size=24, color=LIME)
    current_y += LINE_HEIGHT
    
    rules = [
        '• 三扇门中有一扇门后面是汽车，其他两扇是山羊',
        '• 选择一扇门后，主持人会打开一扇有山羊的门',
        '• 然后你可以选择换门或坚持原选择'
    ]
    
    for rule in rules:
        showMessage(rule, LEFT_COLUMN_X, current_y, font_size=16, color=WHITE)
        current_y += LINE_HEIGHT - 5

def show_statistics():
    """显示统计信息 - 在顶部右侧"""
    stats_y = 70
    clear_area(RIGHT_COLUMN_X, stats_y - 10, RIGHT_COLUMN_WIDTH, 120)
    draw_panel_background(RIGHT_COLUMN_X - 10, stats_y - 10, RIGHT_COLUMN_WIDTH - 50, 120)
    
    current_y = stats_y
    showMessage('📊 游戏统计', RIGHT_COLUMN_X, current_y, font_size=24, color=LIME)
    current_y += LINE_HEIGHT
    
    # 第一行统计
    showMessage(f'总数:{numOfGames} 胜:{numOfWins} 负:{numOfGames - numOfWins}', 
               RIGHT_COLUMN_X, current_y, font_size=18, color=WHITE)
    current_y += LINE_HEIGHT
    
    # 策略统计
    showMessage(f'换门: {numOfWinsBySwap}/{numOfSwaps}', RIGHT_COLUMN_X, current_y, font_size=18, color=CYAN)
    showMessage(f'坚持: {numOfWins - numOfWinsBySwap}/{numOfGames - numOfSwaps}', 
               RIGHT_COLUMN_X + 150, current_y, font_size=18, color=CYAN)
    current_y += LINE_HEIGHT
    
    # 胜率
    if numOfSwaps > 0:
        swap_rate = (numOfWinsBySwap / numOfSwaps * 100)
        showMessage(f'换门胜率: {swap_rate:.1f}%', RIGHT_COLUMN_X, current_y, font_size=16, color=YELLOW)
    
    no_swap_games = numOfGames - numOfSwaps
    if no_swap_games > 0:
        no_swap_rate = ((numOfWins - numOfWinsBySwap) / no_swap_games * 100)
        showMessage(f'坚持胜率: {no_swap_rate:.1f}%', RIGHT_COLUMN_X + 200, current_y, font_size=16, color=YELLOW)

def show_controls():
    """显示操作说明 - 在底部左侧"""
    control_y = BOTTOM_SECTION_Y
    clear_area(LEFT_COLUMN_X, control_y, LEFT_COLUMN_WIDTH, 150)
    draw_panel_background(LEFT_COLUMN_X - 10, control_y - 10, LEFT_COLUMN_WIDTH - 200, 100)
    
    current_y = control_y
    showMessage('🎮 操作说明:', LEFT_COLUMN_X, current_y+10, font_size=24, color=LIME)
    current_y += LINE_HEIGHT + 5
    
    controls = [
        '按 1、2、3 键选择对应的门',
        '按 Y 键换门，按 N 键坚持',
        '按 Q 键开始新游戏'
    ]
    
    for control in controls:
        showMessage(control, LEFT_COLUMN_X, current_y, font_size=18, color=WHITE)
        current_y += LINE_HEIGHT - 5

def show_choice_feedback(door_num):
    """显示选择反馈 - 在门下方"""
    feedback_y = DOORS_Y + 300
    clear_area(DOOR_AREA_X, feedback_y, 600, 30)
    showMessage(f"✨ 你选择了门 {door_num}", DOOR_AREA_X+220, feedback_y, font_size=22, color=YELLOW)

def show_swap_question():
    """显示换门询问"""
    question_y = DOORS_Y + 300
    clear_area(DOOR_AREA_X, question_y, 600, 60)
    # door_no = door_choice + 1
    showMessage(f'🤔 要换门吗？按 Y 换，按 N 不换', DOOR_AREA_X, question_y, font_size=20, color=LIME)

def show_swap_choice(choice):
    """显示换门选择结果"""
    choice_y = DOORS_Y + 230
    clear_area(DOOR_AREA_X, choice_y, 600, 30)
    if choice == 'swap':
        showMessage('🔄 你选择了换门', DOOR_AREA_X, choice_y+150, font_size=18, color=BLUE)
    else:
        showMessage('✋ 你选择坚持原选择', DOOR_AREA_X, choice_y+150, font_size=18, color=BLUE)

def awardTheGuest(keyValue, doorNumber):
    """处理玩家的最终选择"""
    global numOfSwaps, numOfWinsBySwap
    gameOver = False
    
    show_swap_question()
    pygame.display.update()
    
    while not gameOver:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    show_swap_choice('stay')
                    pygame.display.update()
                    time.sleep(sleepTime)
                    validate(keyValue)
                    revealImage(keyValue)
                    pygame.display.update()
                    gameOver = True
                    break

                if event.key == pygame.K_y:
                    numOfSwaps += 1
                    show_swap_choice('swap')
                    pygame.display.update()
                    for i in range(3):
                        if i not in [doorNumber, keyValue]:
                            time.sleep(sleepTime)
                            result = validate(i)
                            revealImage(i)
                            if result == 1:
                                numOfWinsBySwap += 1
                            pygame.display.update()
                            gameOver = True
                            break

            if event.type == pygame.QUIT:
                gameOver = True
                pygame.quit()
                quit()
                break

def main():
    """主游戏循环"""
    play = False
    
    # 尝试播放背景音乐
    try:
        pygame.mixer.music.load(gameSound)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except:
        print("无法播放背景音乐，继续游戏...")
    
    # 显示开始画面
    gameDisplay.blit(startImage, startImageRect)
    displayImage(135, 50, promptImage)
    showMessage('press Enter to start.', display_width // 2 - 100, display_height - 100, 
               font_size=36, color=LIME)
    pygame.display.update()
    
    # 等待玩家按下Enter键
    while not play:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    play = True
                    break
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                break

    # 主游戏循环
    while not gameExit:
        gameOver = False
        gameDisplay.fill(BLACK)
        gameDisplay.blit(backgroundImage, backgroundRect)
        
        # 显示各个区域（按区域分层显示）
        show_title()
        show_game_rules()
        show_statistics()
        
        # 显示三扇门（确保在中央清晰区域）
        displayStartImages()
        
        # 显示底部控制说明
        show_controls()
        
        # 绘制分割线（可选，调试用）
        # draw_section_dividers()
        
        pygame.display.update()
        setImagesRandomly()
        
        # 游戏输入处理循环
        while not gameOver:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        gameOver = True
                        break
                    
                    # 处理门的选择
                    door_choice = None
                    
                    if event.key == pygame.K_1:
                        door_choice = 0
                        door_num = 1
                        show_choice_feedback(1)
                    elif event.key == pygame.K_2:
                        door_choice = 1
                        door_num = 2
                        show_choice_feedback(2)
                    elif event.key == pygame.K_3:
                        door_choice = 2
                        door_num = 3
                        show_choice_feedback(3)
                    
                    if door_choice is not None:
                        displayImage(coordinates[door_choice][0], coordinates[door_choice][1] + 120, chosenImage)
                        pygame.display.update()
                        time.sleep(sleepTime)
                        revealedDoor = displayGoat(door_choice)
                        if revealedDoor is not None:
                            time.sleep(sleepTime)
                            pygame.display.update()
                            time.sleep(sleepTime)
                            awardTheGuest(door_choice, revealedDoor)
                            # 更新统计显示
                            show_statistics()

                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                    break
            
            clock.tick(FPS)

if __name__ == "__main__":
    main()
