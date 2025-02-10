from PIL import Image

def convert_to_100_percent(image_input, scale_percent, output_path=None):
    """
    将不同缩放比例截取的图片转换为100%缩放比的真实尺寸
    
    参数：
    image_input (str/PIL.Image) - 图片路径或PIL.Image对象
    scale_percent (int/float) - 截图时的系统缩放比例（如150表示150%缩放）
    output_path (str, 可选) - 输出路径，不传则返回PIL.Image对象
    
    返回：
    PIL.Image对象（当output_path为空时）
    """
    # 打开图片
    if isinstance(image_input, str):
        img = Image.open(image_input)
    else:
        img = image_input
    
    # 计算缩放因子
    scale_factor = scale_percent / 100.0
    
    if scale_factor <= 0:
        raise ValueError("缩放比例必须大于0")
    
    # 计算新尺寸
    original_width, original_height = img.size
    new_width = round(original_width / scale_factor)
    new_height = round(original_height / scale_factor)
    
    # 使用高质量插值算法调整尺寸
    resized_img = img.resize(
        (new_width, new_height),
        resample=Image.Resampling.LANCZOS
    )
    
    # 保存或返回结果
    if output_path:
        resized_img.save(output_path)
        print(f"图片已保存至：{output_path}")
    else:
        return resized_img

# 使用示例
if __name__ == "__main__":
    # 示例：将150%缩放截取的图片转换
    input_image = "125.png"
    output_image = "100.png"
    
    convert_to_100_percent(
        image_input=input_image,
        scale_percent=125,
        output_path=output_image
    )