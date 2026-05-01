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
    
    # 确定文件路径
    # 如果是GitHub Actions环境，在src目录生成
    # 如果是本地运行，在上级目录生成
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        m3u_path = "playlist.m3u"
        log_path = "update.log"
        check_path = "last_check.txt"
    else:
        m3u_path = "../playlist.m3u"
        log_path = "../update.log"
        check_path = "../last_check.txt"
    
    # 读取现有文件内容（用于比较）
    old_content = ""
    if os.path.exists(m3u_path):
        with open(m3u_path, 'r', encoding='utf-8') as f:
            old_content = f.read()
    
    # 获取网页内容
    m3u_text = fetch_webpage(URL)
    if not m3u_text:
        logger.error("无法获取节目源，更新失败")
        return
    
    # 解析频道
    groups = parse_channels(m3u_text)
    if not groups:
        logger.error("没有找到有效频道")
        return
    
    # 生成新内容
    new_content = generate_m3u_content(groups)
    
    # 检查是否有变化
    if has_changes(old_content, new_content):
        logger.info("检测到内容变化，更新文件")
        save_m3u(groups, m3u_path)
        
        # 如果是GitHub Actions环境，执行Git操作
        if os.environ.get('GITHUB_ACTIONS') == 'true':
            # 在GitHub Actions中，文件已在当前目录
            pass
    else:
        logger.info("内容无变化，无需更新")
    
    # 保存检查时间
    with open(check_path, 'w') as f:
        f.write(datetime.now().isoformat())
    
    logger.info("检查完成")
