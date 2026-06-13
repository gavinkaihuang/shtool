import os
from datetime import datetime, timedelta

races = [
    {
        "name": "澳大利亚大奖赛",
        "sessions": [
            {"type": "三练", "date": "3.7", "time": "09:30", "duration_hours": 1},
            {"type": "排位赛", "date": "3.7", "time": "13:00", "duration_hours": 1},
            {"type": "正赛", "date": "3.8", "time": "12:00", "duration_hours": 2}
        ]
    },
    {
        "name": "中国大奖赛",
        "sessions": [
            {"type": "冲刺赛", "date": "3.14", "time": "11:00", "duration_hours": 1},
            {"type": "排位赛", "date": "3.14", "time": "15:00", "duration_hours": 1},
            {"type": "正赛", "date": "3.15", "time": "15:00", "duration_hours": 2}
        ]
    },
    {
        "name": "日本大奖赛",
        "sessions": [
            {"type": "三练", "date": "3.28", "time": "10:30", "duration_hours": 1},
            {"type": "排位赛", "date": "3.28", "time": "14:00", "duration_hours": 1},
            {"type": "正赛", "date": "3.29", "time": "13:00", "duration_hours": 2}
        ]
    },
    {
        "name": "巴林大奖赛",
        "sessions": [
            {"type": "三练", "date": "4.11", "time": "20:30", "duration_hours": 1},
            {"type": "排位赛", "date": "4.12", "time": "00:00", "duration_hours": 1},
            {"type": "正赛", "date": "4.12", "time": "23:00", "duration_hours": 2}
        ]
    },
    {
        "name": "沙特阿拉伯大奖赛",
        "sessions": [
            {"type": "三练", "date": "4.18", "time": "21:30", "duration_hours": 1},
            {"type": "排位赛", "date": "4.19", "time": "01:00", "duration_hours": 1},
            {"type": "正赛", "date": "4.20", "time": "01:00", "duration_hours": 2}
        ]
    },
    {
        "name": "美国-迈阿密大奖赛",
        "sessions": [
            {"type": "冲刺赛", "date": "5.3", "time": "00:00", "duration_hours": 1},
            {"type": "排位赛", "date": "5.3", "time": "04:00", "duration_hours": 1},
            {"type": "正赛", "date": "5.4", "time": "04:00", "duration_hours": 2}
        ]
    },
    {
        "name": "加拿大大奖赛",
        "sessions": [
            {"type": "冲刺赛", "date": "5.24", "time": "00:00", "duration_hours": 1},
            {"type": "排位赛", "date": "5.24", "time": "04:00", "duration_hours": 1},
            {"type": "正赛", "date": "5.25", "time": "04:00", "duration_hours": 2}
        ]
    },
    {
        "name": "摩纳哥大奖赛",
        "sessions": [
            {"type": "三练", "date": "6.6", "time": "18:30", "duration_hours": 1},
            {"type": "排位赛", "date": "6.6", "time": "22:00", "duration_hours": 1},
            {"type": "正赛", "date": "6.7", "time": "21:00", "duration_hours": 2}
        ]
    },
    {
        "name": "西班牙-巴塞罗那大奖赛",
        "sessions": [
            {"type": "三练", "date": "6.13", "time": "18:30", "duration_hours": 1},
            {"type": "排位赛", "date": "6.13", "time": "22:00", "duration_hours": 1},
            {"type": "正赛", "date": "6.14", "time": "21:00", "duration_hours": 2}
        ]
    },
    {
        "name": "奥地利大奖赛",
        "sessions": [
            {"type": "三练", "date": "6.27", "time": "18:30", "duration_hours": 1},
            {"type": "排位赛", "date": "6.27", "time": "22:00", "duration_hours": 1},
            {"type": "正赛", "date": "6.28", "time": "21:00", "duration_hours": 2}
        ]
    },
    {
        "name": "英国大奖赛",
        "sessions": [
            {"type": "冲刺赛", "date": "7.4", "time": "19:00", "duration_hours": 1},
            {"type": "排位赛", "date": "7.4", "time": "23:00", "duration_hours": 1},
            {"type": "正赛", "date": "7.5", "time": "22:00", "duration_hours": 2}
        ]
    },
    {
        "name": "比利时大奖赛",
        "sessions": [
            {"type": "三练", "date": "7.18", "time": "18:30", "duration_hours": 1},
            {"type": "排位赛", "date": "7.18", "time": "22:00", "duration_hours": 1},
            {"type": "正赛", "date": "7.19", "time": "21:00", "duration_hours": 2}
        ]
    },
    {
        "name": "匈牙利大奖赛",
        "sessions": [
            {"type": "三练", "date": "7.25", "time": "18:30", "duration_hours": 1},
            {"type": "排位赛", "date": "7.25", "time": "22:00", "duration_hours": 1},
            {"type": "正赛", "date": "7.26", "time": "21:00", "duration_hours": 2}
        ]
    },
    {
        "name": "荷兰大奖赛",
        "sessions": [
            {"type": "冲刺赛", "date": "8.22", "time": "18:00", "duration_hours": 1},
            {"type": "排位赛", "date": "8.22", "time": "22:00", "duration_hours": 1},
            {"type": "正赛", "date": "8.23", "time": "21:00", "duration_hours": 2}
        ]
    },
    {
        "name": "意大利大奖赛",
        "sessions": [
            {"type": "三练", "date": "9.5", "time": "18:30", "duration_hours": 1},
            {"type": "排位赛", "date": "9.5", "time": "22:00", "duration_hours": 1},
            {"type": "正赛", "date": "9.6", "time": "21:00", "duration_hours": 2}
        ]
    },
    {
        "name": "西班牙-马德里大奖赛",
        "sessions": [
            {"type": "三练", "date": "9.12", "time": "18:30", "duration_hours": 1},
            {"type": "排位赛", "date": "9.12", "time": "22:00", "duration_hours": 1},
            {"type": "正赛", "date": "9.13", "time": "21:00", "duration_hours": 2}
        ]
    },
    {
        "name": "阿塞拜疆大奖赛",
        "sessions": [
            {"type": "三练", "date": "9.25", "time": "16:30", "duration_hours": 1},
            {"type": "排位赛", "date": "9.25", "time": "20:00", "duration_hours": 1},
            {"type": "正赛", "date": "9.26", "time": "19:00", "duration_hours": 2}
        ]
    },
    {
        "name": "新加坡大奖赛",
        "sessions": [
            {"type": "冲刺赛", "date": "10.10", "time": "17:00", "duration_hours": 1},
            {"type": "排位赛", "date": "10.10", "time": "21:00", "duration_hours": 1},
            {"type": "正赛", "date": "10.11", "time": "20:00", "duration_hours": 2}
        ]
    },
    {
        "name": "美国大奖赛",
        "sessions": [
            {"type": "三练", "date": "10.25", "time": "01:30", "duration_hours": 1},
            {"type": "排位赛", "date": "10.25", "time": "05:00", "duration_hours": 1},
            {"type": "正赛", "date": "10.26", "time": "04:00", "duration_hours": 2}
        ]
    },
    {
        "name": "墨西哥大奖赛",
        "sessions": [
            {"type": "三练", "date": "11.1", "time": "01:30", "duration_hours": 1},
            {"type": "排位赛", "date": "11.1", "time": "05:00", "duration_hours": 1},
            {"type": "正赛", "date": "11.2", "time": "04:00", "duration_hours": 2}
        ]
    },
    {
        "name": "圣保罗大奖赛",
        "sessions": [
            {"type": "三练", "date": "11.7", "time": "22:30", "duration_hours": 1},
            {"type": "排位赛", "date": "11.8", "time": "02:00", "duration_hours": 1},
            {"type": "正赛", "date": "11.9", "time": "01:00", "duration_hours": 2}
        ]
    },
    {
        "name": "拉斯维加斯大奖赛",
        "sessions": [
            {"type": "三练", "date": "11.21", "time": "08:30", "duration_hours": 1},
            {"type": "排位赛", "date": "11.21", "time": "12:00", "duration_hours": 1},
            {"type": "正赛", "date": "11.22", "time": "12:00", "duration_hours": 2}
        ]
    },
    {
        "name": "卡塔尔大奖赛",
        "sessions": [
            {"type": "三练", "date": "11.28", "time": "22:30", "duration_hours": 1},
            {"type": "排位赛", "date": "11.29", "time": "02:00", "duration_hours": 1},
            {"type": "正赛", "date": "11.30", "time": "00:00", "duration_hours": 2}
        ]
    },
    {
        "name": "阿布扎比大奖赛",
        "sessions": [
            {"type": "三练", "date": "12.5", "time": "18:30", "duration_hours": 1},
            {"type": "排位赛", "date": "12.5", "time": "22:00", "duration_hours": 1},
            {"type": "正赛", "date": "12.6", "time": "21:00", "duration_hours": 2}
        ]
    }
]

def format_utc(dt):
    return dt.strftime("%Y%m%dT%H%M%SZ")

def generate_ics():
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//F1 2026 Calendar//CN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:F1 2026 赛程",
        "X-WR-TIMEZONE:UTC"
    ]
    
    now_str = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    
    for i, race in enumerate(races, 1):
        for session in race["sessions"]:
            # Parse Beijing Time
            month, day = map(int, session["date"].split('.'))
            hour, minute = map(int, session["time"].split(':'))
            
            local_dt = datetime(2026, month, day, hour, minute)
            
            # Convert to UTC (Beijing time - 8 hours)
            utc_start = local_dt - timedelta(hours=8)
            utc_end = utc_start + timedelta(hours=session["duration_hours"])
            
            summary = f"F1 {race['name']} - {session['type']}"
            uid = f"f1-2026-gp-{i}-{session['type']}-{session['date']}@huangkai.shtool"
            
            lines.extend([
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{now_str}",
                f"DTSTART:{format_utc(utc_start)}",
                f"DTEND:{format_utc(utc_end)}",
                f"SUMMARY:{summary}",
                "DESCRIPTION:F1 2026 赛季赛程",
                "STATUS:CONFIRMED",
                "SEQUENCE:0",
                "END:VEVENT"
            ])
            
    lines.append("END:VCALENDAR")
    
    output_path = os.path.join(os.path.dirname(__file__), "F1_2026_Calendar.ics")
    with open(output_path, "w", encoding="utf-8") as f:
        # RFC 5545 specifies that lines should be separated by CRLF (\r\n)
        f.write("\r\n".join(lines) + "\r\n")
    print(f"Calendar successfully generated at: {output_path}")

if __name__ == "__main__":
    generate_ics()
