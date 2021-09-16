def find_java_from_where():
    import os
    result = os.popen("where java").read()
    result = result[:-1]
    # 由于返回结果会在末尾加上换行，因此需要删除
    # result = result.replace("java.exe", "javaw.exe")
    return result

# 暂时先这么着，之后再完善了
