# -*- coding: utf-8 -*-
"""checkpoint — 用已驗證的 ExportZPrj 存檔。API 不可用時清楚報告, 不假裝成功。"""
import os

def save(clo, ckpt_dir, name, logger):
    os.makedirs(ckpt_dir, exist_ok=True)
    path = os.path.join(ckpt_dir, name)
    try:
        res = clo.export_zprj(path)
        logger.ok(f"checkpoint saved: {name}")
        logger.info(str(res))
        return True
    except Exception as ex:
        logger.warn(f"checkpoint NOT saved ({name}): {ex}")
        logger.info("ExportZPrj unavailable in this build — save manually via File > Save Project As.")
        return False
