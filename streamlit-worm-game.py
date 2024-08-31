import streamlit as st
import pandas as pd
import numpy as np
import time

# 게임 상태를 저장할 세션 상태 변수들
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'worm' not in st.session_state:
    st.session_state.worm = {
        'x': 400,
        'y': 300,
        'radius': 15,
        'thickness': 1,
        'speed': 3,
        'length': 20,
        'segments': []
    }
if 'foods' not in st.session_state:
    st.session_state.foods = []
if 'game_started' not in st.session_state:
    st.session_state.game_started = False

# 음식 타입 정의
food_types = {
    'grains': ['🍚', '🍜', '🍝', '🍞', '🥐', '🥖', '🥨', '🥯', '🥞', '🧇', '🌽', '🌾', '🥔', '🍠'],
    'proteins': ['🥩', '🍗', '🍖', '🍤', '🍳', '🥚', '🧀', '🥜', '🫘', '🍣', '🐟', '🦐', '🦀', '🦞'],
    'veggiesFruits': ['🥦', '🥬', '🥒', '🍅', '🍆', '🥕', '🌶️', '🫑', '🥔', '🍠', '🍎', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🫐', '🍑', '🍍'],
    'dairy': ['🥛', '🧃', '🥤']
}

def create_food():
    food_type = np.random.choice(list(food_types.keys()))
    return {
        'x': np.random.randint(20, 780),
        'y': np.random.randint(20, 580),
        'type': food_type,
        'emoji': np.random.choice(food_types[food_type])
    }

def spawn_food():
    if len(st.session_state.foods) < 15:
        st.session_state.foods.append(create_food())

def eat_food(food):
    old_length = st.session_state.worm['length']
    if food['type'] == 'grains':
        st.session_state.worm['speed'] += 0.2
    elif food['type'] == 'proteins':
        st.session_state.worm['thickness'] += 0.1
        st.session_state.worm['speed'] = max(1, st.session_state.worm['speed'] - 0.1)
    elif food['type'] == 'veggiesFruits':
        st.session_state.worm['length'] = max(10, st.session_state.worm['length'] - 2)
    elif food['type'] == 'dairy':
        st.session_state.worm['length'] += 2
    
    if st.session_state.worm['length'] > old_length:
        st.session_state.score += (st.session_state.worm['length'] - old_length) * 10
    elif st.session_state.worm['length'] < old_length:
        st.session_state.score = max(0, st.session_state.score - (old_length - st.session_state.worm['length']) * 5)

def check_collision():
    to_remove = []
    for i, food in enumerate(st.session_state.foods):
        dx = food['x'] - st.session_state.worm['x']
        dy = food['y'] - st.session_state.worm['y']
        distance = np.sqrt(dx**2 + dy**2)
        if distance < st.session_state.worm['radius'] * st.session_state.worm['thickness'] + 15:
            eat_food(food)
            to_remove.append(i)
    
    for i in reversed(to_remove):
        st.session_state.foods.pop(i)

def move_worm(mouse_x, mouse_y):
    dx = mouse_x - st.session_state.worm['x']
    dy = mouse_y - st.session_state.worm['y']
    distance = np.sqrt(dx**2 + dy**2)
    
    if distance > st.session_state.worm['speed']:
        st.session_state.worm['x'] += (dx / distance) * st.session_state.worm['speed']
        st.session_state.worm['y'] += (dy / distance) * st.session_state.worm['speed']
    else:
        st.session_state.worm['x'] = mouse_x
        st.session_state.worm['y'] = mouse_y
    
    st.session_state.worm['segments'].insert(0, (st.session_state.worm['x'], st.session_state.worm['y']))
    while len(st.session_state.worm['segments']) > st.session_state.worm['length']:
        st.session_state.worm['segments'].pop()

def main():
    st.set_page_config(page_title="귀여운 지렁이 게임", layout="wide")
    
    st.title("귀여운 지렁이 게임")
    
    # 게임 규칙 표시
    st.sidebar.header("게임 규칙")
    st.sidebar.write("1. 지렁이는 마우스를 따라 움직입니다.")
    st.sidebar.write("2. 곡류를 먹으면 속도가 빨라집니다.")
    st.sidebar.write("3. 고기생선달걀콩류를 먹으면 두꺼워지고 속도가 느려집니다.")
    st.sidebar.write("4. 과일류와 채소류를 먹으면 길이가 짧아집니다.")
    st.sidebar.write("5. 우유유제품류를 먹으면 길어집니다.")
    st.sidebar.write("6. 지렁이의 길이가 길어질수록 점수가 올라갑니다.")
    st.sidebar.write("7. 지렁이의 길이가 짧아지면 점수가 감소합니다.")
    
    if not st.session_state.game_started:
        if st.button("게임 시작"):
            st.session_state.game_started = True
    
    if st.session_state.game_started:
        # 게임 화면
        game_area = st.empty()
        
        # 점수 표시
        score_text = st.empty()
        
        # 마우스 위치 입력
        col1, col2 = st.columns(2)
        with col1:
            mouse_x = st.slider("X 위치", 0, 800, 400)
        with col2:
            mouse_y = st.slider("Y 위치", 0, 600, 300)
        
        # 게임 업데이트
        spawn_food()
        move_worm(mouse_x, mouse_y)
        check_collision()
        
        # 게임 화면 업데이트
        game_state = pd.DataFrame({
            'x': [segment[0] for segment in st.session_state.worm['segments']] + [food['x'] for food in st.session_state.foods],
            'y': [segment[1] for segment in st.session_state.worm['segments']] + [food['y'] for food in st.session_state.foods],
            'type': ['worm'] * len(st.session_state.worm['segments']) + [food['type'] for food in st.session_state.foods],
            'emoji': ['🐛'] * len(st.session_state.worm['segments']) + [food['emoji'] for food in st.session_state.foods]
        })
        
        def color_cells(val):
            if val == 'worm':
                return 'background-color: #ff9ff3'
            elif val == 'grains':
                return 'background-color: #ffeaa7'
            elif val == 'proteins':
                return 'background-color: #fab1a0'
            elif val == 'veggiesFruits':
                return 'background-color: #55efc4'
            elif val == 'dairy':
                return 'background-color: #81ecec'
            else:
                return ''
        
        styled_game_state = game_state.style.applymap(color_cells, subset=['type'])
        game_area.dataframe(styled_game_state, height=600)
        
        # 점수 업데이트
        score_text.text(f"점수: {st.session_state.score}")
        
        # 게임 리셋 버튼
        if st.button("게임 리셋"):
            st.session_state.score = 0
            st.session_state.worm = {
                'x': 400,
                'y': 300,
                'radius': 15,
                'thickness': 1,
                'speed': 3,
                'length': 20,
                'segments': []
            }
            st.session_state.foods = []
            st.experimental_rerun()

if __name__ == "__main__":
    main()
