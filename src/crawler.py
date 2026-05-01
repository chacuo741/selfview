# 在文件顶部添加路径配置
import os

# 配置
URL = "http://rihou.cc:555/gggg.nzk/"
M3U_FILENAME = "playlist.m3u"
LAST_CHECK_FILE = "last_check.txt"
LOG_FILE = "update.log"

def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("开始检查节目源更新")
    
    # 检查是否需要更新
    if should_run_update():
        logger.info("距离上次检查已超过7天，开始更新")
    else:
        logger.info("距离上次检查不足7天，跳过更新")
        return
    
    # 重要修正：确保文件在当前目录生成
    # 无论是本地还是GitHub Actions，都在src目录生成
    m3u_path = M3U_FILENAME  # 在src目录下
    check_path = LAST_CHECK_FILE
    log_path = LOG_FILE
    
    logger.info(f"文件将生成在: {os.path.abspath('.')}")
    logger.info(f"M3U文件路径: {m3u_path}")
    
    # 获取网页内容
    m3u_text = fetch_webpage(URL)
    if not m3u_text:
        logger.error("无法获取节目源，更新失败")
        return

    # 解析频道
    logger.info("解析节目源频道……")
    groups = parse_channels(m3u_text)
    if not groups:
        logger.error("无有效频道，退出")
        return

    logger.info("生成M3U文件……")
    save_m3u(groups, m3u_path)
    
    # 保存检查时间
    with open(check_path, 'w') as f:
        f.write(datetime.now().isoformat())
    
    logger.info("检查完成")
