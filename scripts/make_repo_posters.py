#!/usr/bin/env python
"""Generate landscape and portrait posters for the repository."""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
GALLERY = ROOT / "assets" / "gallery"
POSTERS = ROOT / "assets" / "posters"
POSTERS.mkdir(parents=True, exist_ok=True)

TITLE_EN = "Academic Review Decksmith"
TITLE_CN = "学术综述汇报工坊"
TAGLINE_EN = "Turn scholarly review drafts into citation-aware, presentation-ready research slides."
TAGLINE_CN = "将综述初稿、论文资料与 PPT 模板转化为结构严谨、图表公式可解释的学术汇报。"
REPO_DISPLAY = "Academic Review Decksmith | 学术综述汇报工坊"


def git_remote_url() -> str:
    moved_url = "https://github.com/ficooooo/Paper2ScholarSlides"
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        url = result.stdout.strip()
        if "Academic-Review-Decksmith--Turn-Literature-Reviews-into-Rigorous--Citation-Aware-Research-Slides" in url:
            return moved_url
        return url.removesuffix(".git")
    except Exception:
        return moved_url


REMOTE_URL = git_remote_url()

BG = "#F4F8FB"
PANEL = "#FFFFFF"
NAVY = "#103A5D"
BLUE = "#2A72B8"
TEAL = "#2D9C90"
ORANGE = "#D9771E"
RED = "#D7263D"
SLATE = "#5D6B78"
TEXT = "#1F2A33"
LINE = "#D7E2EC"
PALE_BLUE = "#EDF5FC"
PALE_GREEN = "#EDF9F6"
PALE_ORANGE = "#FFF6EC"
PALE_RED = "#FFF0F2"


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc"
    return ImageFont.truetype(path, size)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        current = ""
        for ch in paragraph:
            trial = current + ch
            bbox = draw.textbbox((0, 0), trial, font=font)
            if bbox[2] - bbox[0] <= max_width or not current:
                current = trial
            else:
                lines.append(current)
                current = ch
        if current:
            lines.append(current)
    return lines


def draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font, fill: str, max_width: int, line_gap: int = 8):
    x, y = xy
    lines = wrap_text(draw, text, font, max_width)
    h = 0
    for line in lines:
        draw.text((x, y + h), line, font=font, fill=fill)
        bbox = draw.textbbox((x, y + h), line if line else "A", font=font)
        h += (bbox[3] - bbox[1]) + line_gap
    return h


def rounded_panel(base: Image.Image, box: tuple[int, int, int, int], fill: str = PANEL, outline: str = LINE, radius: int = 28, shadow: bool = True):
    x1, y1, x2, y2 = box
    if shadow:
        shadow_img = Image.new("RGBA", base.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        shadow_draw.rounded_rectangle((x1 + 8, y1 + 12, x2 + 8, y2 + 12), radius=radius, fill=(10, 42, 78, 24))
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(10))
        base.alpha_composite(shadow_img)
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)


def badge(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, fill: str, color: str = NAVY):
    draw.rounded_rectangle(box, radius=18, fill=fill, outline=None)
    font = load_font(24, bold=True)
    tw = draw.textbbox((0, 0), text, font=font)[2]
    th = draw.textbbox((0, 0), text, font=font)[3]
    x1, y1, x2, y2 = box
    draw.text((x1 + (x2 - x1 - tw) / 2, y1 + (y2 - y1 - th) / 2 - 2), text, font=font, fill=color)


def pill_row(draw, start_x, y, labels):
    x = start_x
    for text, fill, color in labels:
        font = load_font(24, bold=True)
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0] + 42
        badge(draw, (x, y, x + w, y + 42), text, fill, color)
        x += w + 16


def feature_card(base: Image.Image, box, title_en, title_cn, body, accent, bg_fill):
    rounded_panel(base, box, fill=bg_fill, outline=accent, radius=24, shadow=False)
    draw = ImageDraw.Draw(base)
    x1, y1, x2, y2 = box
    draw.rounded_rectangle((x1 + 18, y1 + 18, x1 + 46, y1 + 46), radius=8, fill=accent)
    draw.text((x1 + 60, y1 + 14), title_en, font=load_font(28, bold=True), fill=NAVY)
    draw.text((x1 + 60, y1 + 52), title_cn, font=load_font(20, bold=False), fill=SLATE)
    draw_wrapped(draw, (x1 + 20, y1 + 92), body, load_font(20), TEXT, x2 - x1 - 40, line_gap=6)


def labeled_image_panel(base: Image.Image, box, title, image_path: Path, footer: str):
    rounded_panel(base, box, fill=PANEL, outline=LINE, radius=28, shadow=True)
    draw = ImageDraw.Draw(base)
    x1, y1, x2, y2 = box
    draw.text((x1 + 22, y1 + 18), title, font=load_font(28, bold=True), fill=NAVY)
    inner = (x1 + 20, y1 + 68, x2 - 20, y2 - 58)
    img = Image.open(image_path).convert("RGB")
    target_w = inner[2] - inner[0]
    target_h = inner[3] - inner[1]
    img.thumbnail((target_w, target_h))
    paste_x = inner[0] + (target_w - img.width) // 2
    paste_y = inner[1] + (target_h - img.height) // 2
    base.paste(img, (paste_x, paste_y))
    draw.text((x1 + 22, y2 - 40), footer, font=load_font(18), fill=SLATE)


def workflow_panel(base: Image.Image, box):
    rounded_panel(base, box, fill=PANEL, outline=LINE, radius=28, shadow=True)
    draw = ImageDraw.Draw(base)
    x1, y1, x2, y2 = box
    draw.text((x1 + 24, y1 + 18), "Workflow | 工作流", font=load_font(30, bold=True), fill=NAVY)
    labels = [
        ("Sources", "论文 / 初稿 / 模板", BLUE),
        ("Map", "图表 / 公式 / 证据", TEAL),
        ("Argument", "背景 -> 机理 -> 模型 -> 控制", ORANGE),
        ("Deck", "PPTX 页面 / 原生组件", RED),
        ("QA", "PNG 导出 / 文本扫描 / 来源检查", NAVY),
    ]
    cx = x1 + 28
    cy = y1 + 98
    gap = 20
    bw = (x2 - x1 - 56 - gap * 4) // 5
    bh = 118
    for idx, (head, sub, color) in enumerate(labels):
        bx1 = cx + idx * (bw + gap)
        bx2 = bx1 + bw
        rounded_panel(base, (bx1, cy, bx2, cy + bh), fill="#FBFDFF", outline=color, radius=18, shadow=False)
        draw.text((bx1 + 16, cy + 14), head, font=load_font(24, bold=True), fill=color)
        draw_wrapped(draw, (bx1 + 16, cy + 52), sub, load_font(18), TEXT, bw - 30, line_gap=4)
        if idx < len(labels) - 1:
            ax = bx2 + 6
            ay = cy + bh // 2
            draw.line((ax, ay, ax + gap - 10, ay), fill=BLUE, width=5)
            draw.polygon([(ax + gap - 10, ay), (ax + gap - 24, ay - 8), (ax + gap - 24, ay + 8)], fill=BLUE)


def repo_panel(base: Image.Image, box):
    rounded_panel(base, box, fill=PANEL, outline=LINE, radius=28, shadow=True)
    draw = ImageDraw.Draw(base)
    x1, y1, x2, y2 = box
    draw.text((x1 + 24, y1 + 20), "Repository | 仓库信息", font=load_font(30, bold=True), fill=NAVY)
    draw.text((x1 + 24, y1 + 78), "Title / 标题", font=load_font(20, bold=True), fill=SLATE)
    draw_wrapped(draw, (x1 + 24, y1 + 110), REPO_DISPLAY, load_font(26, bold=True), NAVY, x2 - x1 - 48, 6)
    draw.text((x1 + 24, y1 + 178), "GitHub / 项目地址", font=load_font(20, bold=True), fill=SLATE)
    draw_wrapped(draw, (x1 + 24, y1 + 210), REMOTE_URL, load_font(15), TEXT, x2 - x1 - 48, 3)
    draw.text((x1 + 24, y2 - 34), "Codex Skill · PPTX · Figure QA · Formula Notes · Public-safe Assets", font=load_font(18), fill=SLATE)


def usecase_panel(base: Image.Image, box):
    rounded_panel(base, box, fill=PANEL, outline=LINE, radius=28, shadow=True)
    draw = ImageDraw.Draw(base)
    x1, y1, x2, y2 = box
    draw.text((x1 + 24, y1 + 18), "Best For | 适用场景", font=load_font(28, bold=True), fill=NAVY)
    entries = [
        "课程综述汇报  Course review talks",
        "实验室组会      Lab seminars",
        "博士生初审      PhD-level review talks",
        "学位答辩支持    Thesis defense support",
        "期刊 Club       Journal-club presentations",
    ]
    yy = y1 + 74
    for idx, text in enumerate(entries):
        draw.rounded_rectangle((x1 + 24, yy + idx * 50, x1 + 44, yy + 20 + idx * 50), radius=6, fill=[BLUE, TEAL, ORANGE, RED, NAVY][idx % 5])
        draw.text((x1 + 58, yy - 4 + idx * 50), text, font=load_font(22), fill=TEXT)


def output_panel(base: Image.Image, box):
    rounded_panel(base, box, fill=PANEL, outline=LINE, radius=28, shadow=True)
    draw = ImageDraw.Draw(base)
    x1, y1, x2, y2 = box
    draw.text((x1 + 24, y1 + 18), "Outputs | 输出物", font=load_font(28, bold=True), fill=NAVY)
    lines = [
        "SKILL.md: 通用综述转汇报规则",
        "README: 项目介绍与上手方式",
        "Gallery: 概览图、效果图、图件预览",
        "Figures: 学术风格自绘图件库",
        "Template: 公共发布安全版学术模板",
        "Scripts: 文本扫描、海报生成、概览图生成",
    ]
    draw_wrapped(draw, (x1 + 24, y1 + 72), "\n".join(lines), load_font(20), TEXT, x2 - x1 - 48, 8)


def add_header(base: Image.Image, size: tuple[int, int], portrait: bool = False):
    draw = ImageDraw.Draw(base)
    w, h = size
    header_h = 300 if not portrait else 310
    draw.rounded_rectangle((0, 0, w, header_h), radius=0, fill=NAVY)
    draw.text((90, 48), TITLE_EN, font=load_font(68 if not portrait else 62, bold=True), fill="white")
    draw.text((90, 126 if not portrait else 120), TITLE_CN, font=load_font(36 if not portrait else 34, bold=True), fill="#DCEBFA")
    draw_wrapped(draw, (90, 168 if not portrait else 168), TAGLINE_EN, load_font(24), "#EAF3FB", w - 180, 6)
    draw_wrapped(draw, (90, 202 if not portrait else 220), TAGLINE_CN, load_font(24), "#BFD7EA", w - 180, 6)
    labels = [
        ("Codex Skill", PALE_BLUE, NAVY),
        ("Review-to-Deck", PALE_GREEN, NAVY),
        ("Citation-aware", PALE_ORANGE, NAVY),
        ("Formula Notes", PALE_RED, NAVY),
    ]
    pill_y = header_h - 56 if not portrait else header_h - 58
    pill_row(draw, 90, pill_y, labels)


def build_landscape():
    size = (2400, 1350)
    base = Image.new("RGBA", size, BG)
    add_header(base, size, portrait=False)

    feature_boxes = [
        (90, 340, 760, 515),
        (790, 340, 1460, 515),
        (90, 540, 760, 715),
        (790, 540, 1460, 715),
        (90, 740, 760, 915),
        (790, 740, 1460, 915),
    ]
    feature_texts = [
        ("Rebuild Argument", "重构综述叙事", "从“章节堆叠”转为“问题—机理—结构—模型—控制—应用”的学术讲述顺序。", BLUE, PALE_BLUE),
        ("Figure Logic", "图件按来源分层", "区分文献原图、重绘图、原生 PPT 组件与公开安全示意图，避免图文混乱。", TEAL, PALE_GREEN),
        ("Formula Notes", "公式含义直观解释", "关键公式不只展示，还说明变量、物理意义、控制量和工程约束。", ORANGE, PALE_ORANGE),
        ("Template Fidelity", "模板风格保真", "沿用标题栏、配色、页码、留白与表格语言，同时保持内容可编辑。", RED, PALE_RED),
        ("Export QA", "导出预览校验", "导出 PNG 联系图检查溢出、遮挡、低对比度、图像压缩和错误占位文本。", BLUE, PALE_BLUE),
        ("Public-safe Release", "公开发布安全资产", "提供通用模板、项目概览图、海报与图件预览，便于 GitHub 展示与传播。", TEAL, PALE_GREEN),
    ]
    for box, data in zip(feature_boxes, feature_texts):
        feature_card(base, box, *data)

    repo_panel(base, (1500, 340, 2310, 580))
    labeled_image_panel(base, (1500, 605, 2310, 920), "Workflow Preview | 项目概览", GALLERY / "project-overview.png", "Repo overview banner")
    labeled_image_panel(base, (1500, 945, 1900, 1270), "Figures | 图件系统", GALLERY / "academic-figures-overview.png", "Academic figure pack")
    labeled_image_panel(base, (1910, 945, 2310, 1270), "Deck Preview | 效果预览", GALLERY / "snake-robot-demo-overview.png", "Synthetic poster-safe deck overview")

    workflow_panel(base, (90, 950, 1460, 1170))
    usecase_panel(base, (90, 1190, 670, 1330))
    output_panel(base, (700, 1190, 1460, 1330))

    draw = ImageDraw.Draw(base)
    draw.text((1510, 1292), "GitHub URL", font=load_font(22, bold=True), fill=SLATE)
    draw_wrapped(draw, (1658, 1290), REMOTE_URL, load_font(15), TEXT, 640, 3)

    out = POSTERS / "academic-review-decksmith-poster-landscape.png"
    base.convert("RGB").save(out, quality=95)
    return out


def build_portrait():
    size = (1700, 2500)
    base = Image.new("RGBA", size, BG)
    add_header(base, size, portrait=True)

    repo_panel(base, (70, 370, 1630, 650))
    workflow_panel(base, (70, 680, 1630, 920))

    features = [
        (70, 950, 800, 1155),
        (830, 950, 1630, 1155),
        (70, 1180, 800, 1385),
        (830, 1180, 1630, 1385),
        (70, 1410, 800, 1615),
        (830, 1410, 1630, 1615),
    ]
    feature_texts = [
        ("Review-to-Deck", "综述转汇报", "把综述初稿、论文资料和模板转成可讲、可审、可展示的学术汇报页面。", BLUE, PALE_BLUE),
        ("Citation-aware", "来源感知图件", "每张关键图片都明确其角色：平台证据、方法示意、实验结果或重绘逻辑图。", TEAL, PALE_GREEN),
        ("Formula Meaning", "公式含义说明", "用短注释解释模型项、控制量、变量关系和使用边界，而不是把公式当装饰。", ORANGE, PALE_ORANGE),
        ("Editable Layout", "原生组件可编辑", "分类表、流程图、矩阵和标签尽量用 PPT 原生文本框与形状构成。", RED, PALE_RED),
        ("Visual QA", "可验证的导出检查", "导出预览图逐页审查遮挡、对齐、清晰度和占位文本，减少交付风险。", BLUE, PALE_BLUE),
        ("Public-safe Assets", "适合公开发布", "提供海报、项目概览、通用模板和图件库，兼顾展示效果与版权风险控制。", TEAL, PALE_GREEN),
    ]
    for box, data in zip(features, feature_texts):
        feature_card(base, box, *data)

    labeled_image_panel(base, (70, 1650, 790, 2070), "Project Overview | 项目概览", GALLERY / "project-overview.png", "Hero banner used in README")
    labeled_image_panel(base, (830, 1650, 1630, 2070), "Figure Gallery | 图件预览", GALLERY / "academic-figures-overview.png", "Preview of publication-style figures")
    labeled_image_panel(base, (70, 2095, 1630, 2390), "Deck Preview | 效果图", GALLERY / "snake-robot-demo-overview.png", "Synthetic poster-safe deck overview")

    draw = ImageDraw.Draw(base)
    footer_y = 2410
    draw.text((70, footer_y), "Repository / 仓库标题", font=load_font(22, bold=True), fill=SLATE)
    draw.text((330, footer_y), REPO_DISPLAY, font=load_font(22, bold=True), fill=NAVY)
    draw.text((70, footer_y + 36), "GitHub", font=load_font(22, bold=True), fill=SLATE)
    draw_wrapped(draw, (170, footer_y + 34), REMOTE_URL, load_font(18), TEXT, 1450, 3)

    out = POSTERS / "academic-review-decksmith-poster-portrait.png"
    base.convert("RGB").save(out, quality=95)
    return out


def main():
    landscape = build_landscape()
    portrait = build_portrait()
    print(landscape)
    print(portrait)


if __name__ == "__main__":
    main()
