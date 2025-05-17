# kurup - A simple, markdown-based note taking application
# Copyright (C) 2025 Davis Thomas Daniel
#
# This file is part of kurup.
#
# kurup is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kurup is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kurup. If not, see <https://www.gnu.org/licenses/>.

import random

def get_random_label(param):
    if param =='note':
        return random.choice(note_area_labels)
    elif param=='heading':
        return random.choice(heading_labels)


note_area_labels = [
    "What's on your mind?",
    "Type away, word wizard!",
    "Jot it like it’s hot!",
    "Make your mark here...",
    "Let the thoughts flow!",
    "Write something legendary!",
    "Notepad of destiny...",
    "Keyboard ready... go!",
    "Tell your tale here...",
    "Unleash your imagination!",
    "Your thoughts, your canvas!",
    "Words are magic, start casting!",
    "Type like nobody’s watching!",
    "Brain dump in 3...2...1...",
    "Ready, set, type!",
    "Time to write your masterpiece!",
    "Create something awesome!",
    "This is where the magic happens!",
]

heading_labels = [
    "Your thoughts, beautifully trapped.",
    "Organizing chaos, one note at a time.",
    "Like a diary, but less emotional.",
    "Smart enough to pretend it’s AI.",
    "I won't ghost your notes. Promise.",
    "Because even geniuses need a good place for notes.",
    "For all those thoughts you thought you’d forget.",
    "The only place your ideas can’t escape.",
    "Because writing it down just makes it real.",
    "Because sometimes your best idea is the one you almost forgot.",
    "Noteworthy in every way except the puns",
    "Like sticky notes, but they actually stick around.",
    "Where thoughts check in but never check out.",
    "Thought-hoarder's anonymous, digital edition.",
    "Because writing on your palm is so last century.",
    "Separating the noteworthy from the not-worthy."
    ]
