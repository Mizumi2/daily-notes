import json
import os
import random
from datetime import datetime, timezone

LOG_FILE = os.environ.get("LOG_FILE", "learning-log.md")
STATE_FILE = os.environ.get("STATE_FILE", ".cache/activity_state.json")
RUN_SLOT = os.environ.get("RUN_SLOT", "")

#在这里调概率
WEEKDAY_FIRST_PROB = 0.90
WEEKDAY_SECOND_PROB = 0.35
WEEKEND_FIRST_PROB = 0.20
WEEKEND_SECOND_PROB = 0.05

FIRST_SLOT = "17 13 * * *"
SECOND_SLOT = "41 16 * * *"


def ensure_file(path: str, default_content: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(default_content)


def load_state():
    ensure_file(STATE_FILE, "{}")
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def ensure_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("# Learning Log\n\n")


def choose_probability(is_weekday: bool, is_first_run: bool) -> float:
    if is_weekday and is_first_run:
        return WEEKDAY_FIRST_PROB
    if is_weekday and not is_first_run:
        return WEEKDAY_SECOND_PROB
    if not is_weekday and is_first_run:
        return WEEKEND_FIRST_PROB
    return WEEKEND_SECOND_PROB


def main():
    ensure_log()
    state = load_state()

    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    weekday = now.weekday()  # 0=Mon, 6=Sun
    is_weekday = weekday < 5

    is_first_run = RUN_SLOT.strip() == FIRST_SLOT
    is_second_run = RUN_SLOT.strip() == SECOND_SLOT

    if not is_first_run and not is_second_run:
        # 手动运行时，默认当作第一次
        is_first_run = True

    today_state = state.get(today, {"count": 0})
    today_count = today_state.get("count", 0)

    # 防止超出每日上限，这里最多 2 次
    if today_count >= 2:
        print(f"{today} already has 2 entries, skip.")
        return

    prob = choose_probability(is_weekday=is_weekday, is_first_run=is_first_run)
    roll = random.random()

    print(f"Today: {today}, weekday={is_weekday}, first_run={is_first_run}, prob={prob}, roll={roll}")

    if roll >= prob:
        print("Probability check failed, skip commit.")
        return

    entry_no = today_count + 1

    content_pool = [
        "整理了一点学习笔记",
        "补了一条小记录",
        "留下一点今天的痕迹",
        "更新了一小段内容",
        "收集了一条值得回看的信息",
    ]
    note = random.choice(content_pool)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"- {today} #{entry_no}: {note}\n")

    state[today] = {"count": entry_no}
    save_state(state)

    print(f"Appended entry #{entry_no} for {today}.")


if __name__ == "__main__":
    main()
