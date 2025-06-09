
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

# 窗口设置 - 改为可调整大小，保持4:3宽高比
initial_width = 1200
initial_height = 900
display_width = initial_width
display_height = initial_height

# 文件夹路径初始化
media = path.join(path.dirname(__file__), 'media')

# 布局参数函数 - 根据窗口大小动态计算
def calculate_layout():
    """根据当前窗口大小计算所有区域的布局参数"""
    global TITLE_AREA_Y, TITLE_AREA_HEIGHT
    global RULES_AREA_X, RULES_AREA_Y, RULES_AREA_WIDTH, RULES_AREA_HEIGHT
    global STATS_AREA_X, STATS_AREA_Y, STATS_AREA_WIDTH, STATS_AREA_HEIGHT
    global DOOR_AREA_X, DOOR_AREA_Y, DOOR_AREA_WIDTH, DOOR_AREA_HEIGHT
    global DOOR_SPACING, DOOR1_X, DOOR2_X, DOOR3_X, DOORS_Y
    global CONTROLS_AREA_X, CONTROLS_AREA_Y, CONTROLS_AREA_WIDTH, CONTROLS_AREA_HEIGHT
    global FEEDBACK_AREA_X, FEEDBACK_AREA_Y, FEEDBACK_AREA_WIDTH, FEEDBACK_AREA_HEIGHT
    global coordinates
    
    # 使用比例来计算位置，保持布局的相对关系
    w, h = display_width, display_height
    
    # 区域1: 标题区域 (相对位置)
    TITLE_AREA_Y = int(h * 0.02)  # 2% from top
    TITLE_AREA_HEIGHT = int(h * 0.06)  # 6% height
    
    # 区域2: 游戏规则区域 (左上，占左半部分的上方)
    RULES_AREA_X = int(w * 0.04)  # 4% from left
    RULES_AREA_Y = int(h * 0.08)  # 8% from top
    RULES_AREA_WIDTH = int(w * 0.45)  # 45% width
    RULES_AREA_HEIGHT = int(h * 0.13)  # 13% height
    
    # 区域3: 统计区域 (右上)
    STATS_AREA_X = int(w * 0.52)  # 52% from left
    STATS_AREA_Y = int(h * 0.08)  # 8% from top
    STATS_AREA_WIDTH = int(w * 0.44)  # 44% width
    STATS_AREA_HEIGHT = int(h * 0.13)  # 13% height
    
    # 区域4: 门区域 (中央) - 保持门的比例
    door_total_width = min(int(w * 0.7), int(h * 0.6))  # 限制最大尺寸
    DOOR_SPACING = door_total_width // 4
    DOOR_AREA_WIDTH = door_total_width
    DOOR_AREA_HEIGHT = int(h * 0.33)  # 33% height
    DOOR_AREA_X = (w - DOOR_AREA_WIDTH) // 2  # 居中
    DOOR_AREA_Y = int(h * 0.25)  # 25% from top
    
    DOOR1_X = DOOR_AREA_X
    DOOR2_X = DOOR_AREA_X + DOOR_SPACING
    DOOR3_X = DOOR_AREA_X + DOOR_SPACING * 2
    DOORS_Y = DOOR_AREA_Y + int(DOOR_AREA_HEIGHT * 0.1)
    
    # 区域5: 操作说明区域 (左下)
    CONTROLS_AREA_X = int(w * 0.04)  # 4% from left
    CONTROLS_AREA_Y = int(h * 0.6)   # 60% from top
    CONTROLS_AREA_WIDTH = int(w * 0.45)  # 45% width
    CONTROLS_AREA_HEIGHT = int(h * 0.35)  # 35% height
    
    # 区域6: 游戏状态反馈区域 (右下)
    FEEDBACK_AREA_X = int(w * 0.52)  # 52% from left
    FEEDBACK_AREA_Y = int(h * 0.6)   # 60% from top
    FEEDBACK_AREA_WIDTH = int(w * 0.44)  # 44% width
    FEEDBACK_AREA_HEIGHT = int(h * 0.35)  # 35% height
    
    # 更新门的坐标
    coordinates = [[DOOR1_X, DOORS_Y], [DOOR2_X, DOORS_Y], [DOOR3_X, DOORS_Y]]

# 初始化布局
calculate_layout()

# 统一的行间距 - 根据窗口大小调整
def get_line_height():
    return max(20, int(display_height * 0.025))

def get_section_gap():
    return max(10, int(display_height * 0.015))

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
game_state = "waiting_for_choice"
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

# 动态创建图片函数 - 根据窗口大小调整
def create_door_image(color, number):
    """创建门的图片 - 根据窗口大小调整"""
    # 门的大小根据可用空间计算
    door_width = max(100, min(150, DOOR_SPACING - 20))
    door_height = max(150, min(200, int(DOOR_AREA_HEIGHT * 0.7)))
    
    surface = pygame.Surface((door_width, door_height))
    surface.fill(color)
    pygame.draw.rect(surface, WHITE, (10, 10, door_width-20, door_height-20), 3)
    pygame.draw.rect(surface, BLACK, (20, 20, door_width-40, door_height-40), 2)
    
    # 门把手
    handle_x = door_width - 30
    handle_y = door_height // 2
    pygame.draw.circle(surface, YELLOW, (handle_x, handle_y), 8)
    
    # 门号码 - 字体大小根据门的大小调整
    font_size = max(36, min(72, door_width // 3))
    font = pygame.font.Font(None, font_size)
    text = font.render(str(number), True, WHITE)
    text_rect = text.get_rect(center=(door_width//2, door_height//2))
    surface.blit(text, text_rect)
    
    return surface

def create_result_image(is_car=True):
    """创建结果图片（汽车或山羊） - 根据窗口大小调整"""
    door_width = max(100, min(150, DOOR_SPACING - 20))
    door_height = max(150, min(200, int(DOOR_AREA_HEIGHT * 0.7)))
    
    surface = pygame.Surface((door_width, door_height))
    if is_car:
        surface.fill(GREEN)
        font_size = max(24, min(36, door_width // 5))
        font = pygame.font.Font(None, font_size)
        text = font.render("CAR", True, WHITE)
        # 绘制简单汽车图形
        car_width = door_width - 60
        car_height = door_height // 5
        car_x = 30
        car_y = door_height // 2 - 20
        pygame.draw.rect(surface, WHITE, (car_x, car_y, car_width, car_height))
        wheel_radius = min(15, car_height // 2)
        pygame.draw.circle(surface, BLACK, (car_x + car_width//4, car_y + car_height + wheel_radius), wheel_radius)
        pygame.draw.circle(surface, BLACK, (car_x + 3*car_width//4, car_y + car_height + wheel_radius), wheel_radius)
    else:
        surface.fill(LIGHT_GRAY)
        font_size = max(24, min(36, door_width // 5))
        font = pygame.font.Font(None, font_size)
        text = font.render("GOAT", True, WHITE)
        # 绘制简单山羊图形
        body_width = door_width - 80
        body_height = door_height // 5
        body_x = 40
        body_y = door_height // 2 - 10
        pygame.draw.ellipse(surface, WHITE, (body_x, body_y, body_width, body_height))
        head_radius = min(20, body_height)
        pygame.draw.circle(surface, WHITE, (body_x + body_width//3, body_y - head_radius//2), head_radius)
        pygame.draw.circle(surface, WHITE, (body_x + 2*body_width//3, body_y - head_radius//2), head_radius)
    
    text_rect = text.get_rect(center=(door_width//2, door_height - 30))
    surface.blit(text, text_rect)
    
    return surface

def create_chosen_image():
    """创建选中标记 - 根据窗口大小调整"""
    door_width = max(100, min(150, DOOR_SPACING - 20))
    chosen_height = max(30, min(50, int(display_height * 0.05)))
    
    surface = pygame.Surface((door_width, chosen_height))
    surface.fill(LIME)
    font_size = max(18, min(28, chosen_height - 4))
    font = pygame.font.Font(None, font_size)
    text = font.render("CHOSEN", True, BLACK)
    text_rect = text.get_rect(center=(door_width//2, chosen_height//2))
    surface.blit(text, text_rect)
    return surface

# 初始化游戏显示
gameDisplay = pygame.display.set_mode((display_width, display_height), RESIZABLE)
pygame.display.set_caption('Monty Hall Problem - 4:3 宽高比')

# 游戏图片 - 将在窗口大小改变时重新创建
doorImageList = []
chosenImage = None
openGoatImage = None
openCarImage = None
possibleImageList = []
imageList = [0, 1, 2]

def recreate_images():
    """重新创建所有图片 - 在窗口大小改变时调用"""
    global doorImageList, chosenImage, openGoatImage, openCarImage, possibleImageList
    
    doorImageList = [
        create_door_image(RED, 1),
        create_door_image(YELLOW, 2),
        create_door_image(BLUE, 3)
    ]
    chosenImage = create_chosen_image()
    openGoatImage = create_result_image(False)
    openCarImage = create_result_image(True)
    possibleImageList = [openCarImage, openGoatImage]

# 初始创建图片
recreate_images()

class FontManager:
    """字体管理器 - 支持中文显示和动态字体大小"""
    
    def __init__(self):
        self.fonts = {}
        self.chinese_font = None
        self.load_fonts()
    
    def load_fonts(self):
        # 尝试加载中文字体
        chinese_font_paths = [
            # Windows 中文字体
            'C:/Windows/Fonts/simsun.ttc',
            'C:/Windows/Fonts/simhei.ttf',
            'C:/Windows/Fonts/msyh.ttc',
            'C:/Windows/Fonts/simkai.ttf',
            # macOS 中文字体
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/Hiragino Sans GB.ttc',
            '/System/Library/Fonts/STHeiti Light.ttc',
            '/System/Library/Fonts/Arial Unicode.ttf',
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
        
        self.preload_common_sizes()
    
    def preload_common_sizes(self):
        """预加载常用字体大小"""
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
        """获取指定大小的字体，支持动态调整"""
        # 根据窗口大小调整字体大小
        adjusted_size = max(12, int(size * min(display_width/1200, display_height/900)))
        
        if adjusted_size not in self.fonts:
            try:
                if self.chinese_font:
                    self.fonts[adjusted_size] = pygame.font.Font(self.chinese_font, adjusted_size)
                else:
                    self.fonts[adjusted_size] = pygame.font.Font(None, adjusted_size)
            except:
                self.fonts[adjusted_size] = pygame.font.Font(None, adjusted_size)
        return self.fonts[adjusted_size]

font_manager = FontManager()

def maintain_aspect_ratio(width, height):
    """维持4:3宽高比，返回调整后的尺寸"""
    target_ratio = 4.0 / 3.0
    current_ratio = width / height
    
    if current_ratio > target_ratio:
        # 太宽，需要根据高度调整宽度
        new_width = int(height * target_ratio)
        new_height = height
    else:
        # 太高，需要根据宽度调整高度
        new_width = width
        new_height = int(width / target_ratio)
    
    # 确保最小尺寸
    min_width, min_height = 800, 600
    if new_width < min_width:
        new_width = min_width
        new_height = int(new_width / target_ratio)
    if new_height < min_height:
        new_height = min_height
        new_width = int(new_height * target_ratio)
    
    return new_width, new_height

def handle_window_resize(new_width, new_height):
    """处理窗口大小改变，保持4:3宽高比"""
    global display_width, display_height, gameDisplay
    
    # 维持4:3宽高比
    display_width, display_height = maintain_aspect_ratio(new_width, new_height)
    
    # 重新创建显示表面
    gameDisplay = pygame.display.set_mode((display_width, display_height), RESIZABLE)
    
    # 重新计算布局
    calculate_layout()
    
    # 重新创建所有图片
    recreate_images()
    
    # print(f"窗口大小调整为: {display_width}x{display_height} (4:3 比例)")

def displayImage(x, y, currentImage):
    """显示图片"""
    gameDisplay.blit(currentImage, (x, y))

def showMessage(message, x, y, font_size=20, color=WHITE):
    """显示消息 - 支持中文和动态字体大小"""
    try:
        font = font_manager.get_font(font_size)
        text_surface = font.render(message, True, color)
        gameDisplay.blit(text_surface, (x, y))
        return text_surface.get_height()
    except Exception as e:
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
    pygame.draw.rect(gameDisplay, (50, 50, 50), (0, TITLE_AREA_Y, display_width, TITLE_AREA_HEIGHT), 1)
    pygame.draw.rect(gameDisplay, (50, 50, 50), (RULES_AREA_X, RULES_AREA_Y, RULES_AREA_WIDTH, RULES_AREA_HEIGHT), 1)
    pygame.draw.rect(gameDisplay, (50, 50, 50), (STATS_AREA_X, STATS_AREA_Y, STATS_AREA_WIDTH, STATS_AREA_HEIGHT), 1)
    pygame.draw.rect(gameDisplay, (50, 50, 50), (DOOR_AREA_X, DOOR_AREA_Y, DOOR_AREA_WIDTH, DOOR_AREA_HEIGHT), 1)
    pygame.draw.rect(gameDisplay, (50, 50, 50), (CONTROLS_AREA_X, CONTROLS_AREA_Y, CONTROLS_AREA_WIDTH, CONTROLS_AREA_HEIGHT), 1)
    pygame.draw.rect(gameDisplay, (50, 50, 50), (FEEDBACK_AREA_X, FEEDBACK_AREA_Y, FEEDBACK_AREA_WIDTH, FEEDBACK_AREA_HEIGHT), 1)

def setImagesRandomly():
    """随机设置门后的物品"""
    randomList = random.sample(range(0, 3), 3)
    imageList[randomList[0]] = possibleImageList[1]  # 山羊
    imageList[randomList[1]] = possibleImageList[0]  # 汽车
    imageList[randomList[2]] = possibleImageList[1]  # 山羊
    # 输出门后物品信息（作弊用）
    for i in range(3):
        if imageList[i] == possibleImageList[0]:  # 汽车
            if i == 0:
                print("door3-alpha")
            elif i == 1:
                print("door1-beta")
            elif i == 2:
                print("door2-gama")


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
    title_x = display_width // 2 - int(display_width * 0.15)
    showMessage('Monty Hall Problem', title_x, TITLE_AREA_Y + 10, font_size=40, color=LIME)

def show_game_rules():
    """区域2: 显示游戏规则"""
    clear_area(RULES_AREA_X, RULES_AREA_Y, RULES_AREA_WIDTH, RULES_AREA_HEIGHT)
    draw_panel_background(RULES_AREA_X, RULES_AREA_Y, RULES_AREA_WIDTH, RULES_AREA_HEIGHT)
    
    current_y = RULES_AREA_Y + 10
    showMessage('游戏规则:', RULES_AREA_X + 10, current_y, font_size=24, color=LIME)
    current_y += get_line_height() + 5
    
    rules = [
        '三扇门中有一扇门后面是汽车，其他两扇是山羊',
        '选择一扇门后，主持人会打开一扇有山羊的门',
        '然后你可以选择换门或坚持原选择'
    ]
    
    for rule in rules:
        showMessage(rule, RULES_AREA_X + 15, current_y, font_size=16, color=WHITE)
        current_y += get_line_height() - 3

def show_statistics():
    """区域3: 显示统计信息"""
    clear_area(STATS_AREA_X, STATS_AREA_Y, STATS_AREA_WIDTH, STATS_AREA_HEIGHT)
    draw_panel_background(STATS_AREA_X, STATS_AREA_Y, STATS_AREA_WIDTH, STATS_AREA_HEIGHT)
    
    current_y = STATS_AREA_Y + 10
    showMessage('游戏统计', STATS_AREA_X + 10, current_y, font_size=24, color=LIME)
    current_y += get_line_height() + 5
    
    # 第一行统计
    showMessage(f'总数:{numOfGames} 胜:{numOfWins} 负:{numOfGames - numOfWins}', 
               STATS_AREA_X + 15, current_y, font_size=18, color=WHITE)
    current_y += get_line_height()
    
    # 策略统计
    showMessage(f'换门: {numOfWinsBySwap}/{numOfSwaps}', STATS_AREA_X + 15, current_y, font_size=18, color=CYAN)
    if STATS_AREA_WIDTH > 300:  # 如果宽度足够，在同一行显示
        showMessage(f'坚持: {numOfWins - numOfWinsBySwap}/{numOfGames - numOfSwaps}', 
                   STATS_AREA_X + STATS_AREA_WIDTH//2, current_y, font_size=18, color=CYAN)
    else:  # 否则换行显示
        current_y += get_line_height()
        showMessage(f'坚持: {numOfWins - numOfWinsBySwap}/{numOfGames - numOfSwaps}', 
                   STATS_AREA_X + 15, current_y, font_size=18, color=CYAN)
    current_y += get_line_height()
    
    # 胜率
    if numOfSwaps > 0:
        swap_rate = (numOfWinsBySwap / numOfSwaps * 100)
        showMessage(f'换门胜率: {swap_rate:.1f}%', STATS_AREA_X + 15, current_y, font_size=16, color=YELLOW)
    
    no_swap_games = numOfGames - numOfSwaps
    if no_swap_games > 0:
        no_swap_rate = ((numOfWins - numOfWinsBySwap) / no_swap_games * 100)
        if STATS_AREA_WIDTH > 300:
            showMessage(f'坚持胜率: {no_swap_rate:.1f}%', STATS_AREA_X + STATS_AREA_WIDTH//2, current_y, font_size=16, color=YELLOW)
        else:
            current_y += get_line_height()
            showMessage(f'坚持胜率: {no_swap_rate:.1f}%', STATS_AREA_X + 15, current_y, font_size=16, color=YELLOW)

def show_controls():
    """区域5: 显示操作说明"""
    clear_area(CONTROLS_AREA_X, CONTROLS_AREA_Y, CONTROLS_AREA_WIDTH, CONTROLS_AREA_HEIGHT)
    draw_panel_background(CONTROLS_AREA_X, CONTROLS_AREA_Y, CONTROLS_AREA_WIDTH, CONTROLS_AREA_HEIGHT)
    
    current_y = CONTROLS_AREA_Y + 10
    showMessage('操作说明:', CONTROLS_AREA_X + 10, current_y, font_size=24, color=LIME)
    current_y += get_line_height() + 5
    
    if game_state == "waiting_for_choice":
        controls = [
            '按 1、2、3 键选择对应的门',
            '按 Q 键开始新游戏',
            '拖拽窗口边缘可调整大小 (保持4:3比例)'
        ]
    elif game_state == "waiting_for_swap":
        controls = [
            '按 Y 键换门，按 N 键坚持',
            '按 Q 键开始新游戏',
            '拖拽窗口边缘可调整大小 (保持4:3比例)'
        ]
    else:  # game_over
        controls = [
            '按 Q 键开始新游戏',
            '游戏结束，查看结果',
            '拖拽窗口边缘可调整大小 (保持4:3比例)'
        ]
    
    for control in controls:
        showMessage(control, CONTROLS_AREA_X + 15, current_y, font_size=18, color=WHITE)
        current_y += get_line_height()

def show_feedback(message, color=WHITE):
    """区域6: 显示游戏状态反馈"""
    clear_area(FEEDBACK_AREA_X, FEEDBACK_AREA_Y, FEEDBACK_AREA_WIDTH, FEEDBACK_AREA_HEIGHT)
    draw_panel_background(FEEDBACK_AREA_X, FEEDBACK_AREA_Y, FEEDBACK_AREA_WIDTH, FEEDBACK_AREA_HEIGHT)
    
    current_y = FEEDBACK_AREA_Y + 10
    showMessage('游戏状态:', FEEDBACK_AREA_X + 10, current_y, font_size=24, color=LIME)
    current_y += get_line_height() + 10
    
    # 支持多行消息
    if isinstance(message, list):
        for msg in message:
            showMessage(msg, FEEDBACK_AREA_X + 15, current_y, font_size=18, color=color)
            current_y += get_line_height()
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
    show_controls()
    pygame.display.update()
    
    return True

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
    title_x = display_width // 2 - int(display_width * 0.16)
    showMessage('Monty Hall Problem', title_x, display_height // 2 - 50, 
               font_size=50, color=LIME)
    
    subtitle_x = display_width // 2 - int(display_width * 0.1)
    showMessage('蒙提霍尔问题', subtitle_x, display_height // 2, 
               font_size=36, color=WHITE)
    
    instruction_x = display_width // 2 - int(display_width * 0.1)
    showMessage('Press Enter to start', instruction_x, display_height // 2 + 50, 
               font_size=32, color=WHITE)
    showMessage('按回车键开始', instruction_x, display_height // 2 + 90, 
               font_size=24, color=YELLOW)
    
    # 窗口大小调整提示 - 更新提示文本
    resize_x = display_width // 2 - int(display_width * 0.16)
    showMessage('拖拽窗口边缘可调整大小 (保持4:3比例)', resize_x, display_height // 2 + 130, 
               font_size=20, color=CYAN)
    
    pygame.display.update()
    
    # 等待玩家按下Enter键
    play = False
    while not play:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    play = True
                    break
            elif event.type == VIDEORESIZE:
                handle_window_resize(event.w, event.h)
                # 重新绘制开始画面
                gameDisplay.fill(BLACK)
                title_x = display_width // 2 - int(display_width * 0.16)
                showMessage('Monty Hall Problem', title_x, display_height // 2 - 50, 
                           font_size=50, color=LIME)
                subtitle_x = display_width // 2 - int(display_width * 0.1)
                showMessage('蒙提霍尔问题', subtitle_x, display_height // 2, 
                           font_size=36, color=WHITE)
                instruction_x = display_width // 2 - int(display_width * 0.1)
                showMessage('Press Enter to start', instruction_x, display_height // 2 + 50, 
                           font_size=32, color=WHITE)
                showMessage('按回车键开始', instruction_x, display_height // 2 + 90, 
                           font_size=24, color=YELLOW)
                resize_x = display_width // 2 - int(display_width * 0.16)
                showMessage('拖拽窗口边缘可调整大小 (保持4:3比例)', resize_x, display_height // 2 + 130, 
                           font_size=20, color=CYAN)
                pygame.display.update()
            elif event.type == pygame.QUIT:
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
        show_title()
        show_game_rules()
        show_statistics()
        displayStartImages()
        show_controls()
        show_feedback("请选择一扇门开始游戏", WHITE)
        
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
                            show_statistics()
                            show_controls()
                            pygame.display.update()
                            
                        elif event.key == pygame.K_y:
                            final_door = handle_swap_choice('swap', swap_key_value, swap_door_number)
                            show_statistics()
                            show_controls()
                            pygame.display.update()
                
                elif event.type == VIDEORESIZE:
                    # 处理窗口大小改变，保持4:3比例
                    handle_window_resize(event.w, event.h)
                    
                    # 重新绘制当前游戏状态
                    gameDisplay.fill(BLACK)
                    show_title()
                    show_game_rules()
                    show_statistics()
                    displayStartImages()
                    show_controls()
                    
                    # 根据当前游戏状态显示相应内容
                    if selected_door is not None:
                        displayImage(coordinates[selected_door][0], 
                                   coordinates[selected_door][1] - 60, chosenImage)
                    
                    if revealed_door is not None:
                        revealImage(revealed_door)
                    
                    # 显示当前状态的反馈
                    if game_state == "waiting_for_choice":
                        show_feedback("请选择一扇门开始游戏", WHITE)
                    elif game_state == "waiting_for_swap":
                        show_swap_question()
                    
                    pygame.display.update()

                elif event.type == pygame.QUIT:
                    gameExit = True
                    gameOver = True
                    break
            
            clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
