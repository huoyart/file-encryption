import random
import hashlib
import base64
import os
# import cv2
# import ffmpeg

std_base64_table = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

# 定义标识码：对应 68 75 6F 79 61 00，即 "huoya" + \x00
ID_CODE = b'\x68\x75\x6F\x79\x61\x00'


# key加密函数
def generate_mod_base64_table(key):
    """根据 key 生成一个魔改 Base64 表"""
    standard_base64_table = list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/")
    # 计算 `key` 的 SHA-256 哈希值
    hash_value = hashlib.sha256(key.encode()).digest()
    # 设定 random.seed()，确保相同 key 产生相同的 Base64 变种
    random.seed(hash_value)
    # 打乱 Base64 表
    random.shuffle(standard_base64_table)
    # print("魔改 Base64 表:", standard_base64_table)  # 调试输出
    return "".join(standard_base64_table)


# 加密函数
def encode_file(input_filename, key):
    """使用魔改 Base64 表加密文件，并在加密数据中加入识别码"""
    mod_base64_table = generate_mod_base64_table(key)
    std_table = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

    # 读取原文件内容（二进制数据）
    with open(input_filename, "rb") as f:
        file_data = f.read()

    # 进行标准 Base64 编码，得到字符串
    std_encoded = base64.b64encode(file_data).decode()
    # 替换为魔改 Base64 字符串
    encode_map = str.maketrans(std_table, mod_base64_table)
    mod_encoded = std_encoded.translate(encode_map)

    # 生成加密后文件名，保留原文件名和后缀
    file_extension = os.path.splitext(input_filename)[-1]  # 文件后缀
    file_name_without_extension = os.path.splitext(input_filename)[0]  # 文件名（不带后缀）
    output_filename = f"{file_name_without_extension}_加密{file_extension}"

    # 将加密后的 Base64 字符串转换为字节，并在前面加上标识码
    final_data = ID_CODE + mod_encoded.encode('utf-8')

    # 保存加密数据，以二进制方式写入
    with open(output_filename, "wb") as f:
        f.write(final_data)

    print(f"🔒 文件 {input_filename} 已加密为 {output_filename}")


# 识别是否加密
def shibie(input_filename):
    with open(input_filename, "rb") as f:
        data = f.read()

    # 检查文件开头是否包含我们的识别码
    if data.startswith(ID_CODE):
        file_state=decode_file(input_filename, "")
        if file_state == "无法识别的文件类型":
            os.remove(output_filename)
            key = input("文件是否含有秘钥，若含有秘钥，请输入秘钥，无秘钥请回车： ").strip()
            decode_file(input_filename, key)
            print("文件已输出，未知文件类型，无法检测解密结果是否正确，请自行确认")
        elif file_state == "文件格式错误":
            while True:
                key = input("解码失败，文件有秘钥，请输入秘钥： ").strip()
                if decode_file(input_filename, key) == "文件格式错误":
                    print("解密文件路径为", output_filename)
                    print("❌秘钥不正确，解密文件后缀与文件头不一致，请检查秘钥")
                else:
                    break
        else:
            print("文件名为", output_filename)
    else:
        print("检测到文件无加密，当前为加密状态")
        key = input("请输入密钥，回车确定，空秘钥可直接回车：").strip()
        encode_file(input_filename, key)


# 解密函数
def decode_file(input_filename, key):
    """解密时自动检测并剥离识别码，然后进行 Base64 解码还原原始数据"""
    mod_base64_table = generate_mod_base64_table(key)
    decode_map = str.maketrans(mod_base64_table, std_base64_table)

    # 以二进制方式读取加密文件
    with open(input_filename, "rb") as f:
        data = f.read()

    # 检查文件开头是否包含我们的识别码
    if data.startswith(ID_CODE):
        data = data[len(ID_CODE):]  # 剥离识别码

    # 剩余数据转换为字符串（应为 Base64 编码后的文本）
    mod_encoded = data.decode('utf-8')

    # 恢复为标准 Base64 编码字符串
    std_encoded = mod_encoded.translate(decode_map)

    # 补齐 '=' 填充（如果缺少）
    padding_needed = len(std_encoded) % 4
    if padding_needed:
        std_encoded += '=' * (4 - padding_needed)

    # Base64 解码恢复原始二进制数据
    decoded_bytes = base64.b64decode(std_encoded)

    # 生成解密后的文件名，保留原始后缀
    file_extension = os.path.splitext(input_filename)[-1]
    file_name_without_extension = os.path.splitext(input_filename)[0]
    global output_filename
    output_filename = f"{file_name_without_extension}_解密{file_extension}"
    with open(output_filename, "wb") as f:
        f.write(decoded_bytes)
    print("输出文件目录", output_filename)
    file_state =guess_file_extension(output_filename)
    if file_state == "无法识别的文件类型":
        return "无法识别的文件类型"
    elif file_state == "文件格式正确":
        return "文件格式正确"
    elif file_state == "文件格式错误":
        return "文件格式错误"

# 检查视频能否正常播放
def check_video_integrity(video_path):
    if guess_file_extension(video_path) == False:
        return False

    print("✅ 视频文件可以正常打开并读取帧。")
    return True
#检查视频能否正常播放


#def check_video_integrity(video_path):
    #print(video_path)
    # cap = cv2.VideoCapture(video_path)
    # if not cap.isOpened():
    #     return False
    #
    # # 尝试读取前几帧
    # frame_count = 0
    # success = True
    # while frame_count < 5 and success:
    #     success, frame = cap.read()
    #     frame_count += 1
    # cap.release()

def guess_file_extension(file_path):
    magic_numbers = {
        # 视频文件
        '.mp4': b'\x00\x00\x00 ',  # MP4 文件（举例）
        '.avi': b'RIFF',  # AVI 文件
        '.mkv': b'\x1aE\xdf\xa3',  # MKV 文件
        '.fiv': b'FLV',  # FIV 文件
        '.flv': b'FLV',  # FLV 文件
        '.mov': b'\x00\x00\x00\x18\x66\x74\x79\x70\x69\x73\x6f\x6d',  # MOV 文件
        '.wmv': b'\x30\x26\xb2\x75\x8e\x66\xcf\x11',  # WMV 文件


        # 压缩文件
        '.zip': b'\x50\x4b\x03\x04',  # ZIP 文件
        '.rar': b'\x52\x61\x72\x21',  # RAR 文件
        '.tar': b'\x75\x73\x74\x61\x72',  # TAR 文件
        '.gz': b'\x1f\x8b',  # GZ 文件
        '.bz2': b'\x42\x5a\x68',  # BZ2 文件
        '.xz': b'\xFD\x37\x7A\x58\x5A\x00',  # XZ 文件

        # 文档文件
        '.pdf': b'\x25\x50\x44\x46',  # PDF 文件
        '.doc': b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1',  # DOC 文件（Microsoft Word）
        '.docx': b'\x50\x4B\x03\x04',  # DOCX 文件（压缩包）
        '.xls': b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1',  # XLS 文件（Microsoft Excel）
        '.xlsx': b'\x50\x4B\x03\x04',  # XLSX 文件（压缩包）
        '.ppt': b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1',  # PPT 文件（Microsoft PowerPoint）
        '.pptx': b'\x50\x4B\x03\x04',  # PPTX 文件（压缩包）

        # 图片文件
        '.mpg': b'\x00\x00\x01\xba',  # MPEG 文件
        '.jpg': b'\xFF\xD8\xFF',  # JPEG 文件
        '.webm': b'\x1a\x45\xdf\xa3',  # WebM 文件
        '.jpeg': b'\xFF\xD8\xFF',  # JPEG 文件
        '.png': b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A',  # PNG 文件
        '.gif': b'GIF87a',  # GIF 文件
        '.bmp': b'\x42\x4D',  # BMP 文件
        '.tiff': b'\x49\x49\x2A\x00',  # TIFF 文件
        '.webp': b'\x52\x49\x46\x46\x00\x00\x00\x00\x57\x45\x42\x50',  # WebP 文件

        # 音频文件
        '.mp3': b'\x49\x44\x33',  # MP3 文件
        '.wav': b'RIFF',  # WAV 文件
        '.ogg': b'\x4F\x67\x67\x53',  # OGG 文件
        '.flac': b'fLaC',  # FLAC 文件

        # 可执行文件
        '.exe': b'\x4D\x5A',  # EXE 文件（Windows 可执行文件）
        '.dll': b'\x4D\x5A',  # DLL 文件（Windows 动态链接库）
        '.so': b'\x7F\x45\x4C\x46',  # SO 文件（Linux 动态链接库）
        '.elf': b'\x7F\x45\x4C\x46',  # ELF 文件（Linux 可执行文件）

        # 文本文件
        '.txt': b'\xEF\xBB\xBF',  # UTF-8 BOM（可选）
        '.csv': b'\xEF\xBB\xBF',  # CSV 文件（如果是 UTF-8 编码）

        # 网络协议
        '.html': b'\x3C\x21\x44\x4F\x43\x54\x59\x50\x45\x20\x48\x54\x4D\x4C',  # HTML 文件
        '.css': b'\x2F\x2A\x20\x43\x53\x53\x20\x46\x69\x6C\x65',  # CSS 文件（注释开始）
        '.js': b'\x2F\x2A\x20\x6A\x61\x76\x61\x53\x63\x72\x69\x70\x74',  # JS 文件（注释开始）
        '.json': b'\x7B\x22',  # JSON 文件（以 { " 开头）
        '.xml': b'\x3C\x3F\x78\x6D\x6C',  # XML 文件（XML 头）
    }

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension not in magic_numbers:
        return "无法识别的文件类型"

    expected_magic_numbers = magic_numbers[file_extension]
    magic_length = len(expected_magic_numbers)

    # 根据文件类型，读取与魔法数字长度匹配的字节
    with open(file_path, "rb") as file:
        file_header = file.read(magic_length)
        # print(file_header)

        if file_header.startswith(expected_magic_numbers):
            print(f"✅{file_extension} 文件格式正确")
            return "文件格式正确"
        else:
            print(f"{file_extension} 文件格式与文件头不一致")
            return "文件格式错误"



# 示例调用


while True:
    filename = input("请输入文件名或拖入文件并回车: ").strip().strip('"')
    if filename ==2:
        break
    try:
        shibie(filename)

    except:
        try:
            if '.' not in filename:
                # 如果文件不存在，我们尝试为其补全后缀
                potential_extensions = ['.mp4', '.avi', '.mkv', '.fiv', '.flv','.mp4', '.mov', '.wmv', '.zip', '.rar','.gz', '.bx', '.xz', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt','.pptx', '.mpg', '.webm', '.jepg', '.png','.gif', '.bmp', '.tiff', '.webp', '.mp3', '.wav', '.ogg', '.flac', '.exe', '.dll', '.elf', '.so','.txt', '.csv', '.html', '.js', '.json','.xml']  # 可根据需要添加其他常见视频格式
                found_valid_extension = False

                for ext in potential_extensions:
                    # 尝试拼接后缀并检查该文件是否存在
                    file_with_extension = filename + ext
                    if os.path.exists(file_with_extension):
                        print(f"✅ 自动检测到文件后缀为 '{ext}'")
                        filename = file_with_extension  # 更新文件路径
                        found_valid_extension = True
                        break
            shibie(filename)
        except Exception as e:

            print("没有"+"'"+str(filename)+"'"+"这个文件")