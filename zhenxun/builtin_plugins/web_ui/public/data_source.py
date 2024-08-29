import os
import shutil
import zipfile
from pathlib import Path

from nonebot.utils import run_sync

from zhenxun.services.log import logger
from zhenxun.utils.http_utils import AsyncHttpx

from .config import COMMAND_NAME, PUBLIC_PATH, TMP_PATH, WEBUI_ASSETS_DOWNLOAD_URL


async def update_webui_assets():
    webui_assets_path = TMP_PATH / "webui_assets.zip"
    if await AsyncHttpx.download_file(
        WEBUI_ASSETS_DOWNLOAD_URL, webui_assets_path, follow_redirects=True
    ):
        logger.info("下载 webui_assets 成功...", COMMAND_NAME)
        return await _file_handle(webui_assets_path)
    raise Exception("下载 webui_assets 失败", COMMAND_NAME)


@run_sync
def _file_handle(webui_assets_path: Path):
    logger.debug("开始解压 webui_assets...", COMMAND_NAME)
    if webui_assets_path.exists():
        tf = zipfile.ZipFile(webui_assets_path)
        tf.extractall(TMP_PATH)
        logger.debug("解压 webui_assets 成功...", COMMAND_NAME)
    else:
        raise Exception("解压 webui_assets 失败，文件不存在...", COMMAND_NAME)
    download_file_path = (
        TMP_PATH / [x for x in os.listdir(TMP_PATH) if (TMP_PATH / x).is_dir()][0]
    )
    shutil.rmtree(PUBLIC_PATH, ignore_errors=True)
    shutil.copytree(download_file_path / "dist", PUBLIC_PATH, dirs_exist_ok=True)
    logger.debug("复制 webui_assets 成功...", COMMAND_NAME)
    shutil.rmtree(TMP_PATH, ignore_errors=True)