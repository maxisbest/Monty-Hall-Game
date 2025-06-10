
import pygame
import sys
from pygame.locals import *
import random
import time
from time import sleep
from datetime import datetime
from os import path

pygame.init()
pygame.mixer.init()

# 窗口设置
display_width = 1200
display_height = 900

# 文件夹路径初始化
media = path.join(path.dirname(__file__), 'media')

# 完全重新设计的布局参数 - 6个明确区域
# 区域1: 标题区域
TITLE_AREA_Y = 20
TITLE_AREA_HEIGHT = 50

# 区域2: 游戏规则区域 (左上)
RULES_AREA_X = 50
RULES_AREA_Y = 70
RULES_AREA_WIDTH = 580
RULES_AREA_HEIGHT = 120

# 区域3: 统计区域 (右上)
STATS_AREA_X = 700
STATS_AREA_Y = 70
STATS_AREA_WIDTH = 450
STATS_AREA_HEIGHT = 120

# 区域4: 门区域 (中央)
DOOR_AREA_X = 200
DOOR_AREA_Y = 220
DOOR_AREA_WIDTH = 800
DOOR_AREA_HEIGHT = 300
DOOR_SPACING = 200
DOOR1_X = DOOR_AREA_X
DOOR2_X = DOOR_AREA_X + DOOR_SPACING
DOOR3_X = DOOR_AREA_X + DOOR_SPACING * 2
DOORS_Y = DOOR_AREA_Y + 20

# 区域5: 操作说明区域 (左下)
CONTROLS_AREA_X = 50
CONTROLS_AREA_Y = 540
CONTROLS_AREA_WIDTH = 580
CONTROLS_AREA_HEIGHT = 150

# 区域6: 游戏状态反馈区域 (右下)
FEEDBACK_AREA_X = 700
FEEDBACK_AREA_Y = 540
FEEDBACK_AREA_WIDTH = 450
FEEDBACK_AREA_HEIGHT = 150

# 统一的行间距
LINE_HEIGHT = 25
SECTION_GAP = 15

clock = pygame.time.Clock()
random.seed(int(datetime.now().timestamp()))

pygame.font.init()

# 游戏状态变量
gameExit = False
gameOver = False
FPS = 100
sleepTime = 0.5
numOfWins = numOfGames = numOfLosses = 0
numOfSwaps = 0
numOfWinsBySwap = 0
door_num = 0
game_state = "waiting_for_choice"  # waiting_for_choice, waiting_for_swap, game_over
selected_door = None
revealed_door = None

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
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (80, 80, 80)

# 创建虚拟图片（用颜色块代替实际图片）
def create_door_image(color, number):
    """创建门的图片"""
    surface = pygame.Surface((150, 200))
    surface.fill(color)
    pygame.draw.rect(surface, WHITE, (10, 10, 130, 180), 3)
    pygame.draw.rect(surface, BLACK, (20, 20, 110, 160), 2)
    
    # 门把手
    pygame.draw.circle(surface, YELLOW, (120, 100), 8)
    
    # 门号码
    font = pygame.font.Font(None, 72)
    text = font.render(str(number), True, WHITE)
    text_rect = text.get_rect(center=(75, 100))
    surface.blit(text, text_rect)
    
    return surface

def create_result_image(is_car=True):
    """创建结果图片（汽车或山羊）"""
    surface = pygame.Surface((150, 200))
    if is_car:
        surface.fill(GREEN)
        font = pygame.font.Font(None, 36)
        text = font.render("CAR", True, WHITE)
        # 绘制简单汽车图形
        pygame.draw.rect(surface, WHITE, (30, 60, 90, 40))
        pygame.draw.circle(surface, WHITE, (50, 110), 15)
        pygame.draw.circle(surface, WHITE, (100, 110), 15)
    else:
        surface.fill(LIGHT_GRAY)
        font = pygame.font.Font(None, 36)
        text = font.render("GOAT", True, WHITE)
        # 绘制简单山羊图形
        pygame.draw.ellipse(surface, WHITE, (40, 70, 70, 40))
        pygame.draw.circle(surface, WHITE, (60, 60), 20)
        pygame.draw.circle(surface, WHITE, (90, 60), 20)
    
    text_rect = text.get_rect(center=(75, 150))
    surface.blit(text, text_rect)
    
    return surface

# 创建游戏图片
door1Image = create_door_image(RED, 1)
door2Image = create_door_image(YELLOW, 2)
door3Image = create_door_image(BLUE, 3)
openGoatImage = create_result_image(False)
openCarImage = create_result_image(True)

# 创建选中标记
def create_chosen_image():
    surface = pygame.Surface((150, 50))
    surface.fill(LIME)
    font = pygame.font.Font(None, 28)
    text = font.render("CHOSEN", True, BLACK)
    text_rect = text.get_rect(center=(75, 25))
    surface.blit(text, text_rect)
    return surface

chosenImage = create_chosen_image()

gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Monty Hall Problem')

doorImageList = [door1Image, door2Image, door3Image]
coordinates = [[DOOR1_X, DOORS_Y], [DOOR2_X, DOORS_Y], [DOOR3_X, DOORS_Y]]
possibleImageList = [openCarImage, openGoatImage]
imageList = [0, 1, 2]

class FontManager:
    """字体管理器 - 支持中文显示"""
    
    def __init__(self):
        self.fonts = {}
        self.chinese_font = None
        self.load_fonts()
    
    def load_fonts(self):
        # 尝试加载中文字体
        chinese_font_paths = [
            # macOS 中文字体
            '/System/Library/Fonts/STHeiti Light.ttc',
            '/System/Library/Fonts/STHeiti Medium.ttc',
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/Hiragino Sans GB.ttc',
            '/System/Library/Fonts/STHeiti Light.ttc',
            '/System/Library/Fonts/Arial Unicode.ttf',
            # Windows 中文字体
            'C:/Windows/Fonts/simsun.ttc',      # 宋体
            'C:/Windows/Fonts/simhei.ttf',      # 黑体
            'C:/Windows/Fonts/msyh.ttc',        # 微软雅黑
            'C:/Windows/Fonts/simkai.ttf',      # 楷体
            # Linux 中文字体
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
            '/usr/share/fonts/truetype/arphic/ukai.ttc',
            '/usr/share/fonts/truetype/arphic/uming.ttc',
            # 相对路径字体
            'fonts/NotoSansCJK-Regular.ttc',
            'fonts/SimHei.ttf',
            'fonts/simsun.ttc'
        ]
        
        # 查找可用的中文字体
        for font_path in chinese_font_paths:
            if path.exists(font_path):
                try:
                    self.chinese_font = font_path
                    print(f"使用中文字体: {font_path}")
                    break
                except:
                    continue
        
        if self.chinese_font is None:
            print("警告: 未找到中文字体，将使用默认字体显示")
        
        # 预加载不同大小的字体
        font_sizes = [16, 18, 20, 22, 24, 28, 32, 40, 50]
        
        for size in font_sizes:
            try:
                if self.chinese_font:
                    font = pygame.font.Font(self.chinese_font, size)
                else:
                    font = pygame.font.Font(None, size)
                self.fonts[size] = font
            except Exception as e:
                print(f"加载字体大小 {size} 失败: {e}")
                self.fonts[size] = pygame.font.Font(None, size)
    
    def get_font(self, size):
        if size not in self.fonts:
            try:
                if self.chinese_font:
                    self.fonts[size] = pygame.font.Font(self.chinese_font, size)
                else:
                    self.fonts[size] = pygame.font.Font(None, size)
            except:
                self.fonts[size] = pygame.font.Font(None, size)
        return self.fonts[size]

font_manager = FontManager()

def displayImage(x, y, currentImage):
    """显示图片"""
    gameDisplay.blit(currentImage, (x, y))

def showMessage(message, x, y, font_size=20, color=WHITE):
    """显示消息 - 支持中文"""
    try:
        font = font_manager.get_font(font_size)
        text_surface = font.render(message, True, color)
        gameDisplay.blit(text_surface, (x, y))
        return text_surface.get_height()
    except Exception as e:
        # 如果中文显示失败，使用英文替代
        print(f"文本显示错误: {e}")
        font = pygame.font.Font(None, font_size)
        text_surface = font.render("Text Display Error", True, color)
        gameDisplay.blit(text_surface, (x, y))
        return text_surface.get_height()

def draw_panel_background(x, y, width, height, alpha=120):
    """绘制半透明背景面板"""
    panel = pygame.Surface((width, height))
    panel.set_alpha(alpha)
    panel.fill((20, 20, 20))
    gameDisplay.blit(panel, (x, y))
    pygame.draw.rect(gameDisplay, LIGHT_GRAY, (x, y, width, height), 2)

def clear_area(x, y, width, height):
    """清除指定区域"""
    pygame.draw.rect(gameDisplay, BLACK, (x, y, width, height))

def draw_area_borders():
    """绘制6个区域的边框（调试用）"""
    # 区域1: 标题
    pygame.draw.rect(gameDisplay, (50, 50, 50), (0, TITLE_AREA_Y, display_width, TITLE_AREA_HEIGHT), 1)
    
    # 区域2: 规则
    pygame.draw.rect(gameDisplay, (50, 50, 50), (RULES_AREA_X, RULES_AREA_Y, RULES_AREA_WIDTH, RULES_AREA_HEIGHT), 1)
    
    # 区域3: 统计
    pygame.draw.rect(gameDisplay, (50, 50, 50), (STATS_AREA_X, STATS_AREA_Y, STATS_AREA_WIDTH, STATS_AREA_HEIGHT), 1)
    
    # 区域4: 门
    pygame.draw.rect(gameDisplay, (50, 50, 50), (DOOR_AREA_X, DOOR_AREA_Y, DOOR_AREA_WIDTH, DOOR_AREA_HEIGHT), 1)
    
    # 区域5: 控制
    pygame.draw.rect(gameDisplay, (50, 50, 50), (CONTROLS_AREA_X, CONTROLS_AREA_Y, CONTROLS_AREA_WIDTH, CONTROLS_AREA_HEIGHT), 1)
    
    # 区域6: 反馈
    pygame.draw.rect(gameDisplay, (50, 50, 50), (FEEDBACK_AREA_X, FEEDBACK_AREA_Y, FEEDBACK_AREA_WIDTH, FEEDBACK_AREA_HEIGHT), 1)

def setImagesRandomly():
    """随机设置门后的物品"""
    randomList = random.sample(range(0, 3), 3)
    imageList[randomList[0]] = possibleImageList[1]  # 山羊
    imageList[randomList[1]] = possibleImageList[0]  # 汽车
    imageList[randomList[2]] = possibleImageList[1]  # 山羊

def displayStartImages():
    """显示初始的门 - 区域4"""
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
    
    if imageList[doorNumber] == openCarImage:
        numOfWins += 1
        numOfGames += 1
        return 1
    else:
        numOfLosses += 1
        numOfGames += 1
        return 0

def show_title():
    """区域1: 显示标题"""
    title_x = display_width // 2 - 200
    showMessage('三门问题--Monty Hall Problem', title_x, TITLE_AREA_Y + 10, font_size=40, color=LIME)

def show_game_rules():
    """区域2: 显示游戏规则"""
    clear_area(RULES_AREA_X, RULES_AREA_Y, RULES_AREA_WIDTH, RULES_AREA_HEIGHT)
    draw_panel_background(RULES_AREA_X, RULES_AREA_Y, RULES_AREA_WIDTH, RULES_AREA_HEIGHT)
    
    current_y = RULES_AREA_Y + 10
    showMessage('游戏规则:', RULES_AREA_X + 10, current_y, font_size=24, color=LIME)
    current_y += LINE_HEIGHT + 5
    
    rules = [
        '三扇门中有一扇门后面是汽车，其他两扇是山羊',
        '选择一扇门后，主持人会打开一扇有山羊的门',
        '然后你可以选择换门或坚持原选择'
    ]
    
    for rule in rules:
        showMessage(rule, RULES_AREA_X + 15, current_y, font_size=16, color=WHITE)
        current_y += LINE_HEIGHT - 3

def show_statistics():
    """区域3: 显示统计信息"""
    clear_area(STATS_AREA_X, STATS_AREA_Y, STATS_AREA_WIDTH, STATS_AREA_HEIGHT)
    draw_panel_background(STATS_AREA_X, STATS_AREA_Y, STATS_AREA_WIDTH, STATS_AREA_HEIGHT)
    
    current_y = STATS_AREA_Y + 10
    showMessage('游戏统计', STATS_AREA_X + 10, current_y, font_size=24, color=LIME)
    current_y += LINE_HEIGHT + 5
    
    # 第一行统计
    showMessage(f'总数:{numOfGames} 胜:{numOfWins} 负:{numOfGames - numOfWins}', 
               STATS_AREA_X + 15, current_y, font_size=18, color=WHITE)
    current_y += LINE_HEIGHT
    
    # 策略统计
    showMessage(f'换门: {numOfWinsBySwap}/{numOfSwaps}', STATS_AREA_X + 15, current_y, font_size=18, color=CYAN)
    showMessage(f'坚持: {numOfWins - numOfWinsBySwap}/{numOfGames - numOfSwaps}', 
               STATS_AREA_X + 200, current_y, font_size=18, color=CYAN)
    current_y += LINE_HEIGHT
    
    # 胜率
    if numOfSwaps > 0:
        swap_rate = (numOfWinsBySwap / numOfSwaps * 100)
        showMessage(f'换门胜率: {swap_rate:.1f}%', STATS_AREA_X + 15, current_y, font_size=16, color=YELLOW)
    
    no_swap_games = numOfGames - numOfSwaps
    if no_swap_games > 0:
        no_swap_rate = ((numOfWins - numOfWinsBySwap) / no_swap_games * 100)
        showMessage(f'坚持胜率: {no_swap_rate:.1f}%', STATS_AREA_X + 200, current_y, font_size=16, color=YELLOW)

def show_controls():
    """区域5: 显示操作说明"""
    clear_area(CONTROLS_AREA_X, CONTROLS_AREA_Y, CONTROLS_AREA_WIDTH, CONTROLS_AREA_HEIGHT)
    draw_panel_background(CONTROLS_AREA_X, CONTROLS_AREA_Y, CONTROLS_AREA_WIDTH, CONTROLS_AREA_HEIGHT)
    
    current_y = CONTROLS_AREA_Y + 10
    showMessage('操作说明:', CONTROLS_AREA_X + 10, current_y, font_size=24, color=LIME)
    current_y += LINE_HEIGHT + 5
    
    if game_state == "waiting_for_choice":
        controls = [
            '按 1、2、3 键选择对应的门',
            '按 Q 键开始新游戏'
        ]
    elif game_state == "waiting_for_swap":
        controls = [
            '按 Y 键换门，按 N 键坚持',
            '按 Q 键开始新游戏'
        ]
    else:  # game_over
        controls = [
            '按 Q 键开始新游戏',
            '游戏结束，查看结果'
        ]
    
    for control in controls:
        showMessage(control, CONTROLS_AREA_X + 15, current_y, font_size=18, color=WHITE)
        current_y += LINE_HEIGHT

def show_feedback(message, color=WHITE):
    """区域6: 显示游戏状态反馈"""
    clear_area(FEEDBACK_AREA_X, FEEDBACK_AREA_Y, FEEDBACK_AREA_WIDTH, FEEDBACK_AREA_HEIGHT)
    draw_panel_background(FEEDBACK_AREA_X, FEEDBACK_AREA_Y, FEEDBACK_AREA_WIDTH, FEEDBACK_AREA_HEIGHT)
    
    current_y = FEEDBACK_AREA_Y + 10
    showMessage('游戏状态:', FEEDBACK_AREA_X + 10, current_y, font_size=24, color=LIME)
    current_y += LINE_HEIGHT + 10
    
    # 支持多行消息
    if isinstance(message, list):
        for msg in message:
            showMessage(msg, FEEDBACK_AREA_X + 15, current_y, font_size=18, color=color)
            current_y += LINE_HEIGHT
    else:
        showMessage(message, FEEDBACK_AREA_X + 15, current_y, font_size=18, color=color)

def show_choice_feedback(door_num):
    """显示选择反馈"""
    show_feedback(f"你选择了门 {door_num}", YELLOW)

def show_swap_question():
    """显示换门询问"""
    show_feedback([
        f"主持人打开了门 {revealed_door + 1}，里面是山羊",
        "要换门吗？按 Y 换，按 N 不换"
    ], LIME)

def show_swap_choice(choice, new_door=None):
    """显示换门选择结果"""
    if choice == 'swap':
        show_feedback(f"你选择了换门到门 {new_door}", BLUE)
    else:
        show_feedback("你选择坚持原选择", BLUE)

def show_game_result(won, door_chosen):
    """显示游戏结果"""
    if won:
        messages = [
            "恭喜你！你赢了！",
            f"门 {door_chosen + 1} 后面确实是汽车！",
            "按 Q 键继续游戏"
        ]
        show_feedback(messages, GREEN)
    else:
        messages = [
            "很遗憾，你输了！",
            f"门 {door_chosen + 1} 后面是山羊",
            "按 Q 键继续游戏"
        ]
        show_feedback(messages, RED)

def awardTheGuest(keyValue, doorNumber):
    """处理玩家的最终选择"""
    global numOfSwaps, numOfWinsBySwap, game_state
    
    game_state = "waiting_for_swap"
    show_swap_question()
    show_controls()  # 更新控制说明
    pygame.display.update()
    
    return True  # 返回True表示需要等待用户输入

def handle_swap_choice(swap_choice, keyValue, doorNumber):
    """处理换门选择"""
    global numOfSwaps, numOfWinsBySwap, game_state
    
    if swap_choice == 'stay':
        show_swap_choice('stay')
        pygame.display.update()
        time.sleep(sleepTime)
        result = validate(keyValue)
        revealImage(keyValue)
        show_game_result(result == 1, keyValue)
        game_state = "game_over"
        return keyValue
    
    elif swap_choice == 'swap':
        numOfSwaps += 1
        # 找到要换到的门
        for i in range(3):
            if i not in [doorNumber, keyValue]:
                show_swap_choice('swap', i + 1)
                pygame.display.update()
                time.sleep(sleepTime)
                result = validate(i)
                revealImage(i)
                if result == 1:
                    numOfWinsBySwap += 1
                show_game_result(result == 1, i)
                game_state = "game_over"
                return i

def main():
    """主游戏循环"""
    global gameExit, game_state, selected_door, revealed_door
    
    # 显示开始画面
    gameDisplay.fill(BLACK)
    showMessage('Monty Hall Problem--三门问题', display_width // 2 - 300, display_height // 2 - 70, 
               font_size=50, color=LIME)
    # showMessage('三门问题--蒙提霍尔问题', display_width // 2 - 140, display_height // 2, 
    #           font_size=36, color=WHITE)
    # showMessage('Press Enter to start', display_width // 2 - 120, display_height // 2 + 50, 
    #           font_size=32, color=WHITE)
    showMessage('按回车键开始', display_width // 2 - 80, display_height // 2 + 90, 
               font_size=24, color=YELLOW)
    pygame.display.update()
    
    # 等待玩家按下Enter键
    play = False
    while not play:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    play = True
                    break
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    # 主游戏循环
    while not gameExit:
        gameOver = False
        game_state = "waiting_for_choice"
        selected_door = None
        revealed_door = None
        
        gameDisplay.fill(BLACK)
        
        # 显示各个区域
        show_title()           # 区域1
        show_game_rules()      # 区域2
        show_statistics()      # 区域3
        displayStartImages()   # 区域4
        show_controls()        # 区域5
        show_feedback("请选择一扇门开始游戏", WHITE)  # 区域6
        
        # 绘制区域边框（调试用，可注释掉）
        # draw_area_borders()
        
        pygame.display.update()
        setImagesRandomly()
        
        waiting_for_swap_input = False
        swap_door_number = None
        swap_key_value = None
        
        # 游戏输入处理循环
        while not gameOver:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        gameOver = True
                        break
                    
                    # 处理门的选择
                    if game_state == "waiting_for_choice":
                        door_choice = None
                        door_num = 0
                        
                        if event.key == pygame.K_1:
                            door_choice = 0
                            door_num = 1
                        elif event.key == pygame.K_2:
                            door_choice = 1
                            door_num = 2
                        elif event.key == pygame.K_3:
                            door_choice = 2
                            door_num = 3
                        
                        if door_choice is not None:
                            selected_door = door_choice
                            show_choice_feedback(door_num)
                            # 显示选中标记
                            displayImage(coordinates[door_choice][0], 
                                       coordinates[door_choice][1] - 60, chosenImage)
                            pygame.display.update()
                            time.sleep(sleepTime)
                            
                            # 显示山羊
                            revealed_door = displayGoat(door_choice)
                            if revealed_door is not None:
                                time.sleep(sleepTime)
                                pygame.display.update()
                                time.sleep(sleepTime)
                                
                                # 准备换门选择
                                waiting_for_swap_input = awardTheGuest(door_choice, revealed_door)
                                swap_key_value = door_choice
                                swap_door_number = revealed_door
                    
                    # 处理换门选择
                    elif game_state == "waiting_for_swap":
                        if event.key == pygame.K_n:
                            final_door = handle_swap_choice('stay', swap_key_value, swap_door_number)
                            show_statistics()  # 更新统计
                            show_controls()    # 更新控制说明
                            pygame.display.update()
                            
                        elif event.key == pygame.K_y:
                            final_door = handle_swap_choice('swap', swap_key_value, swap_door_number)
                            show_statistics()  # 更新统计
                            show_controls()    # 更新控制说明
                            pygame.display.update()

                if event.type == pygame.QUIT:
                    gameExit = True
                    gameOver = True
                    break
            
            clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
