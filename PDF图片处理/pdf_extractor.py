import fitz  # PyMuPDF
import os
import argparse
import sys

def extract_pdf_to_images(pdf_path: str, output_dir: str, dpi: int = 300):
    """
    将 PDF 按页切割并保存为图片
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # 加载 PDF 文档
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"错误: 无法打开 PDF 文件。详细信息: {e}")
        sys.exit(1)
    
    # 默认 PDF 为 72 DPI，通过矩阵缩放提升输出分辨率
    zoom_factor = dpi / 72.0
    matrix = fitz.Matrix(zoom_factor, zoom_factor)
    
    total_pages = len(doc)
    print(f"开始处理，共 {total_pages} 页...")

    for page_num in range(total_pages):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=matrix)
        
        # 补零命名，确保文件系统排序正确 (例如: page_0001.png)
        output_file = os.path.join(output_dir, f"page_{page_num + 1:04d}.png")
        pix.save(output_file)
        print(f"已生成: {output_file}")

    doc.close()
    print(f"处理完成！所有图片已保存至: {output_dir}")

def main():
    parser = argparse.ArgumentParser(
        description="PDF 切图工具：将大型 PDF 文件按页切割为高质量图片，适配 VLM 视觉大模型处理需求。"
    )
    
    parser.add_argument(
        "-i", "--input", 
        required=True, 
        help="必填: 输入的 PDF 文件绝对或相对路径"
    )
    parser.add_argument(
        "-o", "--output", 
        required=True, 
        help="必填: 输出图片的保存目录路径"
    )
    parser.add_argument(
        "-d", "--dpi", 
        type=int, 
        default=300, 
        help="选填: 输出图片的 DPI 分辨率 (默认: 300)"
    )

    args = parser.parse_args()

    # 验证输入文件是否存在
    if not os.path.isfile(args.input):
        print(f"错误: 找不到输入文件 '{args.input}'")
        sys.exit(1)

    extract_pdf_to_images(
        pdf_path=args.input, 
        output_dir=args.output, 
        dpi=args.dpi
    )

if __name__ == "__main__":
    main()