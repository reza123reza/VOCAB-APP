from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton, MDFloatingActionButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.list import MDList, ThreeLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.clock import Clock
from datetime import datetime
from database import Database
from api_service import APIService

# برای صدا
try:
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.INTERNET, Permission.WRITE_EXTERNAL_STORAGE, 
                        Permission.READ_EXTERNAL_STORAGE, Permission.WAKE_LOCK])
    ANDROID = True
except:
    ANDROID = False


class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.current_words = []
        self.current_index = 0
        self.build_ui()
        
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        
        # Header with gradient effect
        header_card = MDCard(
            size_hint_y=None,
            height=dp(180),
            elevation=8,
            md_bg_color=(0.1, 0.5, 0.8, 1),
            radius=[15, 15, 15, 15],
            padding=dp(20)
        )
        
        header_layout = MDBoxLayout(orientation='vertical', spacing=dp(10))
        
        title = MDLabel(
            text="[size=32]📚 Vocabulary Master[/size]",
            markup=True,
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )
        
        stats = self.db.get_statistics()
        
        self.stats_label = MDLabel(
            text=f"[size=18]✅ Learned: {stats['learned']}[/size]",
            markup=True,
            halign="center",
            theme_text_color="Custom",
            text_color=(0.8, 1, 0.8, 1)
        )
        
        self.learning_label = MDLabel(
            text=f"[size=18]📖 Learning: {stats['learning']}[/size]",
            markup=True,
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 0.8, 1)
        )
        
        # Progress percentage
        total = stats['learned'] + stats['learning']
        percentage = (stats['learned'] / total * 100) if total > 0 else 0
        
        self.progress_bar = MDProgressBar(
            value=percentage,
            size_hint_y=None,
            height=dp(8)
        )
        
        header_layout.add_widget(title)
        header_layout.add_widget(self.stats_label)
        header_layout.add_widget(self.learning_label)
        header_layout.add_widget(self.progress_bar)
        
        header_card.add_widget(header_layout)
        
        # Buttons with animations
        buttons_layout = MDBoxLayout(orientation='vertical', spacing=dp(12), padding=dp(10))
        
        self.start_btn = MDRaisedButton(
            text="🚀 Start Today's Practice",
            pos_hint={'center_x': 0.5},
            size_hint_x=0.85,
            size_hint_y=None,
            height=dp(56),
            md_bg_color=(0.2, 0.7, 0.3, 1),
            elevation=4,
            on_release=self.start_daily_practice
        )
        
        add_btn = MDRaisedButton(
            text="➕ Add New Word",
            pos_hint={'center_x': 0.5},
            size_hint_x=0.85,
            size_hint_y=None,
            height=dp(56),
            md_bg_color=(0.2, 0.6, 0.8, 1),
            elevation=4,
            on_release=self.show_add_word_dialog
        )
        
        view_btn = MDRaisedButton(
            text="📋 My Word List",
            pos_hint={'center_x': 0.5},
            size_hint_x=0.85,
            size_hint_y=None,
            height=dp(56),
            md_bg_color=(0.7, 0.4, 0.8, 1),
            elevation=4,
            on_release=self.view_all_words
        )
        
        settings_btn = MDRaisedButton(
            text="⚙️ Settings",
            pos_hint={'center_x': 0.5},
            size_hint_x=0.85,
            size_hint_y=None,
            height=dp(56),
            md_bg_color=(0.5, 0.5, 0.5, 1),
            elevation=4,
            on_release=self.show_settings
        )
        
        buttons_layout.add_widget(self.start_btn)
        buttons_layout.add_widget(add_btn)
        buttons_layout.add_widget(view_btn)
        buttons_layout.add_widget(settings_btn)
        
        layout.add_widget(header_card)
        layout.add_widget(MDLabel(size_hint_y=None, height=dp(10)))
        layout.add_widget(buttons_layout)
        
        self.add_widget(layout)
        
        # انیمیشن دکمه Start
        self.animate_start_button()
    
    def animate_start_button(self):
        """انیمیشن pulse برای دکمه شروع"""
        anim = Animation(elevation=12, duration=0.6) + Animation(elevation=4, duration=0.6)
        anim.repeat = True
        anim.start(self.start_btn)
    
    def start_daily_practice(self, *args):
        # انیمیشن کلیک
        anim = Animation(size_hint_x=0.8, duration=0.1) + Animation(size_hint_x=0.85, duration=0.1)
        anim.start(self.start_btn)
        
        self.current_words = self.db.get_daily_words(10)
        if not self.current_words:
            self.show_dialog("✅ Great Job!", "🎉 No words to practice today!\nYou're doing awesome!")
            return
        
        self.current_index = 0
        self.manager.get_screen('practice').load_word(self.current_words[self.current_index])
        self.manager.transition.direction = 'left'
        self.manager.current = 'practice'
    
    def show_add_word_dialog(self, *args):
        content = MDBoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, height=dp(180))
        
        self.english_input = MDTextField(
            hint_text="English Word",
            mode="rectangle",
            size_hint_y=None,
            height=dp(50)
        )
        
        self.persian_input = MDTextField(
            hint_text="Persian Meaning",
            mode="rectangle",
            size_hint_y=None,
            height=dp(50)
        )
        
        content.add_widget(self.english_input)
        content.add_widget(self.persian_input)
        
        self.add_dialog = MDDialog(
            title="Add New Word",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.add_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="ADD",
                    md_bg_color=(0.2, 0.7, 0.3, 1),
                    on_release=self.add_new_word
                )
            ]
        )
        self.add_dialog.open()
    
    def add_new_word(self, *args):
        english = self.english_input.text.strip()
        persian = self.persian_input.text.strip()
        
        if english and persian:
            self.db.add_word(english, persian)
            self.add_dialog.dismiss()
            self.show_dialog("✅ Success", f"Word '{english}' added successfully!")
            self.update_stats()
        else:
            self.show_toast("Please fill both fields!")
    
    def view_all_words(self, *args):
        self.manager.get_screen('words_list').load_words()
        self.manager.transition.direction = 'left'
        self.manager.current = 'words_list'
    
    def show_settings(self, *args):
        content = MDBoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(150))
        
        content.add_widget(MDLabel(text="Daily words count:", size_hint_y=None, height=dp(30)))
        
        slider_label = MDLabel(text="10 words", halign="center", size_hint_y=None, height=dp(30))
        content.add_widget(slider_label)
        
        dialog = MDDialog(
            title="⚙️ Settings",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())
            ]
        )
        dialog.open()
    
    def show_dialog(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()
    
    def show_toast(self, text):
        from kivymd.toast import toast
        toast(text)
    
    def update_stats(self):
        stats = self.db.get_statistics()
        self.stats_label.text = f"[size=18]✅ Learned: {stats['learned']}[/size]"
        self.learning_label.text = f"[size=18]📖 Learning: {stats['learning']}[/size]"
        
        total = stats['learned'] + stats['learning']
        percentage = (stats['learned'] / total * 100) if total > 0 else 0
        
        # انیمیشن پروگرس بار
        anim = Animation(value=percentage, duration=0.5)
        anim.start(self.progress_bar)
    
    def on_enter(self):
        """هر بار که به این صفحه برمیگردیم آمار رو آپدیت کن"""
        self.update_stats()


class FlippableCard(MDCard):
    """کارت قابل چرخش برای نمایش کلمه"""
    is_flipped = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.95, None)
        self.height = dp(250)
        self.pos_hint = {'center_x': 0.5}
        self.elevation = 10
        self.radius = [20, 20, 20, 20]
        self.padding = dp(20)
        
    def flip(self):
        """چرخش کارت"""
        self.is_flipped = not self.is_flipped
        
        # انیمیشن چرخش
        if self.is_flipped:
            anim = Animation(opacity=0, duration=0.2) + Animation(opacity=1, duration=0.2)
        else:
            anim = Animation(opacity=0, duration=0.2) + Animation(opacity=1, duration=0.2)
        
        anim.start(self)


class PracticeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.api = APIService()
        self.current_word = None
        self.show_answer = False
        self.build_ui()
    
    def build_ui(self):
        main_layout = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Top bar با Progress
        top_bar = MDBoxLayout(size_hint_y=None, height=dp(80), spacing=dp(10))
        
        self.back_btn = MDIconButton(
            icon="arrow-left",
            pos_hint={'center_y': 0.5},
            on_release=self.go_back
        )
        
        progress_layout = MDBoxLayout(orientation='vertical', spacing=dp(5))
        
        self.word_number = MDLabel(
            text="Word 1 of 10",
            halign="center",
            font_style="H6"
        )
        
        self.progress_bar = MDProgressBar(
            value=10,
            size_hint_y=None,
            height=dp(6)
        )
        
        progress_layout.add_widget(self.word_number)
        progress_layout.add_widget(self.progress_bar)
        
        top_bar.add_widget(self.back_btn)
        top_bar.add_widget(progress_layout)
        
        # Scrollable content
        scroll = ScrollView()
        self.content_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            adaptive_height=True,
            padding=dp(10)
        )
        
        # کارت کلمه با قابلیت Flip
        self.word_card = MDCard(
            size_hint=(0.95, None),
            height=dp(280),
            pos_hint={'center_x': 0.5},
            elevation=12,
            radius=[20, 20, 20, 20],
            padding=dp(20),
            md_bg_color=(0.95, 0.95, 1, 1)
        )
        
        self.word_card_layout = MDBoxLayout(orientation='vertical', spacing=dp(15))
        
        # English word
        word_header = MDBoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        
        self.english_label = MDLabel(
            text="",
            halign="center",
            font_style="H3",
            theme_text_color="Primary",
            markup=True
        )
        
        # دکمه اسپیکر با شمارنده
        speaker_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_x=None,
            width=dp(60),
            spacing=dp(2)
        )
        
        self.speaker_btn = MDIconButton(
            icon="volume-high",
            icon_size="40sp",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 0.9, 1),
            on_release=self.play_pronunciation
        )
        
        self.play_count_label = MDLabel(
            text="🔊 0",
            halign="center",
            font_style="Caption",
            size_hint_y=None,
            height=dp(20)
        )
        
        speaker_layout.add_widget(self.speaker_btn)
        speaker_layout.add_widget(self.play_count_label)
        
        word_header.add_widget(MDLabel())  # Spacer
        word_header.add_widget(self.english_label)
        word_header.add_widget(speaker_layout)
        
        # Phonetic
        self.phonetic_label = MDLabel(
            text="",
            halign="center",
            font_style="Subtitle1",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(30)
        )
        
        # Persian (مخفی تا زمان فشردن Show Answer)
        self.persian_label = MDLabel(
            text="",
            halign="center",
            font_style="H5",
            theme_text_color="Custom",
            text_color=(0.2, 0.7, 0.2, 1),
            opacity=0,
            size_hint_y=None,
            height=dp(40)
        )
        
        # دکمه Show Answer
        self.show_answer_btn = MDRaisedButton(
            text="👁️ Show Answer",
            pos_hint={'center_x': 0.5},
            size_hint_x=0.7,
            md_bg_color=(0.3, 0.5, 0.7, 1),
            on_release=self.toggle_answer
        )
        
        self.word_card_layout.add_widget(word_header)
        self.word_card_layout.add_widget(self.phonetic_label)
        self.word_card_layout.add_widget(self.persian_label)
        self.word_card_layout.add_widget(MDLabel())  # Spacer
        self.word_card_layout.add_widget(self.show_answer_btn)
        
        self.word_card.add_widget(self.word_card_layout)
        
        # کارت مثال‌ها
        self.examples_card = MDCard(
            size_hint=(0.95, None),
            height=dp(220),
            pos_hint={'center_x': 0.5},
            elevation=8,
            radius=[15, 15, 15, 15],
            padding=dp(15),
            md_bg_color=(1, 0.98, 0.95, 1)
        )
        
        examples_layout = MDBoxLayout(orientation='vertical', spacing=dp(12))
        
        examples_title = MDLabel(
            text="📝 Example Sentences:",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(30),
            bold=True,
            theme_text_color="Primary"
        )
        
        self.example1_label = MDLabel(
            text="Loading...",
            size_hint_y=None,
            height=dp(70),
            theme_text_color="Secondary"
        )
        
        self.example2_label = MDLabel(
            text="",
            size_hint_y=None,
            height=dp(70),
            theme_text_color="Secondary"
        )
        
        examples_layout.add_widget(examples_title)
        examples_layout.add_widget(self.example1_label)
        examples_layout.add_widget(self.example2_label)
        
        self.examples_card.add_widget(examples_layout)
        
        # Add to content
        self.content_layout.add_widget(self.word_card)
        self.content_layout.add_widget(self.examples_card)
        
        scroll.add_widget(self.content_layout)
        
        # Action buttons با آیکون
        buttons_layout = MDBoxLayout(
            spacing=dp(15),
            size_hint_y=None,
            height=dp(70),
            padding=[dp(15), 0, dp(15), dp(10)]
        )
        
        self.know_btn = MDRaisedButton(
            text="✅ I Know It",
            size_hint_x=0.5,
            md_bg_color=(0.2, 0.8, 0.2, 1),
            elevation=6,
            on_release=self.mark_as_known
        )
        
        self.dont_know_btn = MDRaisedButton(
            text="❌ Don't Know",
            size_hint_x=0.5,
            md_bg_color=(0.9, 0.3, 0.2, 1),
            elevation=6,
            on_release=self.mark_as_unknown
        )
        
        buttons_layout.add_widget(self.know_btn)
        buttons_layout.add_widget(self.dont_know_btn)
        
        main_layout.add_widget(top_bar)
        main_layout.add_widget(scroll)
        main_layout.add_widget(buttons_layout)
        
        self.add_widget(main_layout)
        
        # متغیر شمارش پخش صدا
        self.play_count = 0
    
    def load_word(self, word):
        self.current_word = word
        self.show_answer = False
        self.play_count = 0
        
        # Reset UI
        self.english_label.text = f"[b]{word['english']}[/b]"
        self.persian_label.text = word['persian']
        self.persian_label.opacity = 0
        self.show_answer_btn.text = "👁️ Show Answer"
        self.play_count_label.text = "🔊 0"
        
        # Update progress
        home_screen = self.manager.get_screen('home')
        current_idx = home_screen.current_index + 1
        total = len(home_screen.current_words)
        self.word_number.text = f"Word {current_idx} of {total}"
        
        progress_value = (current_idx / total) * 100
        anim = Animation(value=progress_value, duration=0.3)
        anim.start(self.progress_bar)
        
        # انیمیشن ورود کارت
        self.word_card.opacity = 0
        self.examples_card.opacity = 0
        Animation(opacity=1, duration=0.5).start(self.word_card)
        Animation(opacity=1, duration=0.5, transition='out_bounce').start(self.examples_card)
        
        # Load details
        self.load_word_details(word['english'])
    
    def load_word_details(self, word):
        self.phonetic_label.text = "Loading..."
        self.example1_label.text = "Loading examples..."
        self.example2_label.text = ""
        
        # Get from API
        data = self.api.get_word_details(word)
        
        if data:
            self.phonetic_label.text = f"/{data.get('phonetic', '')}/".replace("//", "")
            
            examples = data.get('examples', [])
            self.example1_label.text = f"1. {examples[0]}" if len(examples) > 0 else "No examples available"
            self.example2_label.text = f"2. {examples[1]}" if len(examples) > 1 else ""
        else:
            self.phonetic_label.text = ""
            self.example1_label.text = "⚠️ Could not load examples\n(Check internet connection)"
            self.example2_label.text = ""
    
    def toggle_answer(self, *args):
        """نمایش/مخفی کردن جواب"""
        if not self.show_answer:
            # نمایش جواب
            anim = Animation(opacity=1, duration=0.3)
            anim.start(self.persian_label)
            self.show_answer_btn.text = "👁️ Hide Answer"
            self.show_answer = True
        else:
            # مخفی کردن جواب
            anim = Animation(opacity=0, duration=0.3)
            anim.start(self.persian_label)
            self.show_answer_btn.text = "👁️ Show Answer"
            self.show_answer = False
    
    def play_pronunciation(self, *args):
        """پخش صدا (هر تعداد باری که بخواد)"""
        if self.current_word:
            # انیمیشن دکمه
            anim = (Animation(icon_size="50sp", duration=0.1) + 
                   Animation(icon_size="40sp", duration=0.1))
            anim.start(self.speaker_btn)
            
            # افزایش شمارنده
            self.play_count += 1
            self.play_count_label.text = f"🔊 {self.play_count}"
            
            # پخش صدا
            success = self.api.play_audio(self.current_word['english'])
            if not success:
                self.show_toast("⚠️ Could not play audio")
    
    def show_toast(self, text):
        from kivymd.toast import toast
        toast(text)
    
    def mark_as_known(self, *args):
        # انیمیشن موفقیت
        anim = Animation(md_bg_color=(0.3, 1, 0.3, 1), duration=0.2) + \
               Animation(md_bg_color=(0.2, 0.8, 0.2, 1), duration=0.2)
        anim.start(self.know_btn)
        
        self.db.update_word_status(self.current_word['id'], True)
        Clock.schedule_once(lambda dt: self.next_word(), 0.3)
    
    def mark_as_unknown(self, *args):
        # انیمیشن
        anim = Animation(md_bg_color=(1, 0.4, 0.3, 1), duration=0.2) + \
               Animation(md_bg_color=(0.9, 0.3, 0.2, 1), duration=0.2)
        anim.start(self.dont_know_btn)
        
        self.db.update_word_status(self.current_word['id'], False)
        Clock.schedule_once(lambda dt: self.next_word(), 0.3)
    
    def next_word(self):
        home_screen = self.manager.get_screen('home')
        home_screen.current_index += 1
        
        if home_screen.current_index < len(home_screen.current_words):
            self.load_word(home_screen.current_words[home_screen.current_index])
        else:
            self.show_completion_dialog()
    
    def show_completion_dialog(self):
        stats = self.db.get_statistics()
        
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            height=dp(150),
            padding=dp(20)
        )
        
        congrats = MDLabel(
            text="🎉 Awesome Work!",
            halign="center",
            font_style="H5",
            size_hint_y=None,
            height=dp(40)
        )
        
        stats_label = MDLabel(
            text=f"Total Learned: {stats['learned']} words\nKeep going! 💪",
            halign="center",
            theme_text_color="Secondary"
        )
        
        content.add_widget(congrats)
        content.add_widget(stats_label)
        
        dialog = MDDialog(
            title="Practice Completed!",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(
                    text="CONTINUE",
                    md_bg_color=(0.2, 0.7, 0.3, 1),
                    on_release=lambda x: self.go_home(dialog)
                )
            ]
        )
        dialog.open()
    
    def go_back(self, *args):
        self.manager.transition.direction = 'right'
        self.manager.current = 'home'
    
    def go_home(self, dialog):
        dialog.dismiss()
        self.manager.transition.direction = 'right'
        self.manager.current = 'home'


class WordsListScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.api = APIService()
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical')
        
        # Header
        header = MDCard(
            size_hint_y=None,
            height=dp(70),
            elevation=5,
            md_bg_color=(0.1, 0.5, 0.8, 1),
            radius=[0, 0, 0, 0]
        )
        
        header_layout = MDBoxLayout(padding=dp(10), spacing=dp(10))
        
        back_btn = MDIconButton(
            icon="arrow-left",
            theme_icon_color="Custom",
            icon_color=(1, 1, 1, 1),
            on_release=lambda x: self.go_back()
        )
        
        title = MDLabel(
            text="My Word List",
            font_style="H5",
            halign="left",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )
        
        header_layout.add_widget(back_btn)
        header_layout.add_widget(title)
        
        header.add_widget(header_layout)
        
        # Search box
        search_card = MDCard(
            size_hint_y=None,
            height=dp(70),
            padding=dp(10),
            elevation=2
        )
        
        self.search_field = MDTextField(
            hint_text="🔍 Search words...",
            mode="rectangle",
            on_text=self.search_words
        )
        
        search_card.add_widget(self.search_field)
        
        # Words list
        self.scroll = ScrollView()
        self.words_list = MDList(spacing=dp(5))
        
        self.scroll.add_widget(self.words_list)
        
        layout.add_widget(header)
        layout.add_widget(search_card)
        layout.add_widget(self.scroll)
        
        self.add_widget(layout)
    
    def load_words(self):
        self.words_list.clear_widgets()
        words = self.db.get_all_words()
        
        for word in words:
            status_icon = "check-circle" if word['learned'] else "book-open-variant"
            status_color = (0.2, 0.8, 0.2, 1) if word['learned'] else (0.9, 0.6, 0.2, 1)
            
            item = ThreeLineAvatarIconListItem(
                IconLeftWidget(
                    icon=status_icon,
                    theme_icon_color="Custom",
                    icon_color=status_color
                ),
                text=f"[b]{word['english']}[/b]",
                secondary_text=word['persian'],
                tertiary_text=f"Reviewed: {word.get('last_review', 'Never')}",
                on_release=lambda x, w=word: self.play_word_audio(w['english'])
            )
            
            # Add speaker button
            speaker_icon = IconRightWidget(
                icon="volume-high",
                on_release=lambda x, w=word: self.play_word_audio(w['english'])
            )
            item.add_widget(speaker_icon)
            
            self.words_list.add_widget(item)
    
    def search_words(self, instance, text):
        """جستجوی کلمات"""
        self.words_list.clear_widgets()
        words = self.db.get_all_words()
        
        filtered = [w for w in words if text.lower() in w['english'].lower() or 
                   text.lower() in w['persian'].lower()]
        
        for word in filtered:
            status_icon = "check-circle" if word['learned'] else "book-open-variant"
            status_color = (0.2, 0.8, 0.2, 1) if word['learned'] else (0.9, 0.6, 0.2, 1)
            
            item = ThreeLineAvatarIconListItem(
                IconLeftWidget(
                    icon=status_icon,
                    theme_icon_color="Custom",
                    icon_color=status_color
                ),
                text=f"[b]{word['english']}[/b]",
                secondary_text=word['persian'],
                tertiary_text=f"Reviewed: {word.get('last_review', 'Never')}"
            )
            
            self.words_list.add_widget(item)
    
    def play_word_audio(self, word):
        """پخش صدای کلمه از لیست"""
        self.api.play_audio(word)
    
    def go_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'home'


class VocabApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Amber"
        
        sm = MDScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(PracticeScreen(name='practice'))
        sm.add_widget(WordsListScreen(name='words_list'))
        
        return sm

if __name__ == '__main__':
    VocabApp().run()
