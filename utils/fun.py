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
    elif param=='quote':
        return random.choice(heading_labels)

def get_tag_colors(n=50):
    tag_colors = [
        "#CC7A7A", "#E6A366", "#D4D466", "#7ACC7A", "#4DD0E1",
        "#7A9FCC", "#9966CC", "#E67ACC", "#B8B8B8", "#4DB6AC",
        "#8FBC8F", "#DAA520", "#5F9EA0", "#6B8E23", "#CD5C5C",
        "#9370DB", "#D2691E", "#B8860B", "#556B2F", "#8A2BE2",
        "#20B2AA", "#8FBC8F", "#CD853F", "#DC143C", "#A0522D",
        "#6A5ACD", "#2E8B57", "#C71585", "#9ACD32", "#FFD700",
        "#32CD32", "#FF6347", "#4B0082", "#8B008B", "#FF8C00",
        "#008B8B", "#228B22", "#DC143C", "#00CED1", "#FF4500",
        "#48D1CC", "#663399", "#BA55D3", "#F4A460", "#008080",
        "#478A3B", "#4169E1", "#C71585", "#4682B4", "#FF7F50"
    ]

    return tag_colors

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
    "Spill the digital tea...",
    "Where typos become poetry.",
    "Go on, write like no one’s going to read it.",
    "Dear diary... just kidding, sort of.",
    "A safe space for chaotic brilliance.",
    "Scribble something genius-ish.",
    "Channel your inner Shakespeare (or not).",
    "Type now, edit never.",
    "No pressure, but this could change the world.",
    "Brainstorm, rainstorm, thoughtstorm—go!",
    "This box loves your nonsense.",
    "Go ahead, write that novel tweet-length."
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
    "Separating the noteworthy from the not-worthy.",
    "The cloud’s least judgmental corner.",
    "Better than scribbles on your hand.",
    "Because napkin notes are not cloud-compatible.",
    "Smarter than paper. Dumber than AI.",
    "The official home of ‘I'll remember this later.’",
    "Where your notes come to overstay their welcome.",
    "Made with 0% judgment, 100% space for ideas."
    ]
