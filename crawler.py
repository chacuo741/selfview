import requests
import os
import subprocess

url = "http://rihou.cc:555/gggg.nzk/"  # 节目源地址


def fetch_webpage(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.encoding = r.apparent_encoding
        r.raise_for_status()
        return r.text
    except Exception as e:
        print("请求失败：", e)
        return ""


def parse_channels(text):
    groups = {}
    current_group = None
    phoenix_channels = []   

    keep_groups = ["央卫咪咕", "特新Pdtv", "欣赏频道", "特闽Hktv", "央卫高码"]

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        if ',' in line and '#genre#' in line:
            current_group = line.split(',', 1)[0].strip()
            if current_group in keep_groups:
                groups.setdefault(current_group, [])
            else:
                current_group = None
            continue

        if current_group and ',' in line:
            channel_name, stream_url = line.split(',', 1)
            channel_name = channel_name.strip()
            stream_url = stream_url.strip()

            # 提取凤凰台
            if current_group == "特新Pdtv" and "凤凰" in channel_name:
                phoenix_channels.append((channel_name, stream_url))
                continue

            if current_group in groups:
                groups[current_group].append((channel_name, stream_url))

    # 凤凰台放到央卫高码最前面
    if phoenix_channels and "央卫高码" in groups:
        groups["央卫高码"] = phoenix_channels + groups["央卫高码"]
    elif phoenix_channels:
        groups["央卫高码"] = phoenix_channels

    return {g: chs for g, chs in groups.items() if chs}


def save_m3u(groups, filename):
    """生成M3U文件 - 自定义组顺序"""
    # ============ 自定义输出顺序（央卫高码放最前面）============
    group_order = ["央卫高码", "央卫咪咕", "特新Pdtv", "欣赏频道", "特闽Hktv"]
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n\n')
        
        for group in group_order:
            if group in groups and groups[group]:
                f.write(f"#{group}\n")
                for channel_name, stream_url in groups[group]:
                    f.write(f'#EXTINF:-1 group-title="{group}", {channel_name}\n')
                    f.write(stream_url + "\n")
    
    total = sum(len(chs) for chs in groups.values())
    print(f"写入文件 {filename} 完成，节目总数：{total} 条。")


def git_commit_and_push(filename):
    subprocess.run(["git", "add", filename])
    subprocess.run(["git", "commit", "-m", "更新 playlist.m3u"])
    subprocess.run(["git", "push"])


def main():
    filename = "playlist.m3u"
    
    print(f"开始抓取节目源：{url}")
    m3u_text = fetch_webpage(url)
    if not m3u_text:
        print("节目源抓取失败，退出")
        return

    print("解析并过滤节目源……")
    groups = parse_channels(m3u_text)
    if not groups:
        print("无有效频道，退出")
        return

    print("生成M3U文件……")
    save_m3u(groups, filename)
    
    git_commit_and_push(filename)


if __name__ == '__main__':
    main()
