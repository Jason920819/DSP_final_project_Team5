""" from PIL import Image, ImageFilter
import numpy as np

def feathering_function(image_path, output_path, blur_radius):
    
    #對圖片邊緣進行反鋸齒處理，並保留透明背景。
    #:param image_path: 輸入圖片路徑
    #:param output_path: 輸出圖片路徑
    #:param blur_radius: 模糊程度（適度輕微即可）
    
    # 開啟圖片並轉換成 RGBA 模式（確保有透明通道）
    image = Image.open(image_path).convert("RGBA")
    
    # 將圖片轉換成 NumPy 陣列以便進行像素處理
    np_image = np.array(image)

    # 建立一個遮罩，用於區分圖片中非黑色的部分
    # 比較每個像素的 RGB 值是否不是黑色（[0, 0, 0]），非黑色的部分標記為 True ==>不會變透明
    # `.any(axis=-1)` 用於檢查 RGB 三個通道是否有任一個不為 0
    non_black_mask = (np_image[:, :, :3] != [0, 0, 0]).any(axis=-1).astype(np.uint8) * 255
    
    # 將非黑色遮罩轉換成 PIL 格式的灰階圖片 (L 模式)
    mask = Image.fromarray(non_black_mask, mode="L")

    # 使用高斯模糊對遮罩進行平滑處理，以柔化非黑色區域邊緣
    smoothed_mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

    # 建立一個全透明的空白圖層，大小與原圖相同
    anti_aliased_image = Image.new("RGBA", image.size, (0, 0, 0, 0))
    
    # 使用處理過的遮罩，將原始圖像的內容複製到全透明背景上
    # `paste` 方法中，`mask` 決定了每個像素的透明度
    #遮罩值為 255 的部分，對應的原始圖像像素會完整複製（不透明）。
   # 遮罩值為 0 的部分，畫布保持全透明。
    #遮罩值介於 0 和 255 之間，則原始圖像像素會部分透明，透明度與遮罩值成比例。
    anti_aliased_image.paste(image, mask=smoothed_mask)

    # 將結果保存為 PNG 格式，保留透明通道
    anti_aliased_image.save(output_path, format="PNG")
    print(f"反鋸齒處理完成，結果已儲存至: {output_path}")

# 設定圖片路徑與輸出路徑
input_path = "./results/After_Magic_wand.png"
output_path = "./results/After_Feathering.png" 

# 執行反鋸齒處理
feathering_function(input_path, output_path, 2)

 """






from PIL import Image, ImageFilter, ImageTk, ImageOps
import numpy as np
import tkinter as tk


def anti_aliasing(image_path, output_path, blur_radius=2):
    """
    對圖片邊緣進行反鋸齒處理，並保留透明背景。
    """
    image = Image.open(image_path).convert("RGBA")
    np_image = np.array(image)
    non_black_mask = (np_image[:, :, :3] != [0, 0, 0]).any(axis=-1).astype(np.uint8) * 255
    mask = Image.fromarray(non_black_mask, mode="L")
    smoothed_mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))
    anti_aliased_image = Image.new("RGBA", image.size, (0, 0, 0, 0))
    anti_aliased_image.paste(image, mask=smoothed_mask)
    anti_aliased_image.save(output_path, format="PNG")
    print(f"反鋸齒處理完成，結果已儲存至: {output_path}")
    return image, anti_aliased_image


def show_images_with_gui(before_image, after_image):
    """
    顯示處理前後的圖片，支援放大、縮小、重置和平移功能，並添加黑色邊框。
    """
    import tkinter as tk
    from PIL import Image, ImageOps, ImageTk

    # 添加黑色邊框
    border_width = 5
    before_image = ImageOps.expand(before_image, border=border_width, fill="black")
    after_image = ImageOps.expand(after_image, border=border_width, fill="black")

    # 創建主視窗
    root = tk.Tk()
    root.title("Image Comparison Viewer")

    # 轉換圖片為 Tkinter 格式
    before_tk = ImageTk.PhotoImage(before_image)
    after_tk = ImageTk.PhotoImage(after_image)

    # 創建畫布
    canvas_before = tk.Canvas(root, width=before_image.width, height=before_image.height)
    canvas_after = tk.Canvas(root, width=after_image.width, height=after_image.height)

    # 顯示圖片
    canvas_before.create_image(0, 0, anchor=tk.NW, image=before_tk)
    canvas_after.create_image(0, 0, anchor=tk.NW, image=after_tk)

    # 放置畫布
    canvas_before.grid(row=0, column=0, padx=10, pady=10)
    canvas_after.grid(row=0, column=1, padx=10, pady=10)

    # 初始化狀態
    scale_factor = 1.0
    min_scale_factor = 1.0  # 最小縮放比例，不能小於初始大小
    offset_x, offset_y = 0, 0

    def zoom(event):
        """滑鼠滾輪放大/縮小圖片"""
        nonlocal scale_factor
        if event.delta > 0:  # 滾輪向上放大
            scale_factor *= 1.1
        elif event.delta < 0 and scale_factor > min_scale_factor:  # 滾輪向下縮小
            scale_factor /= 1.1
        update_canvas()

    def reset_view():
        """重置圖片到初始大小和位置"""
        nonlocal scale_factor, offset_x, offset_y
        scale_factor = 1.0
        offset_x, offset_y = 0, 0
        update_canvas()

    def update_canvas():
        """更新畫布內容，應用縮放效果"""
        scaled_before = before_image.resize(
            (int(before_image.width * scale_factor), int(before_image.height * scale_factor)), Image.Resampling.LANCZOS
        )
        scaled_after = after_image.resize(
            (int(after_image.width * scale_factor), int(after_image.height * scale_factor)), Image.Resampling.LANCZOS
        )

        scaled_before_tk = ImageTk.PhotoImage(scaled_before)
        scaled_after_tk = ImageTk.PhotoImage(scaled_after)

        canvas_before.delete("all")
        canvas_after.delete("all")

        canvas_before.create_image(0, 0, anchor=tk.NW, image=scaled_before_tk)
        canvas_after.create_image(0, 0, anchor=tk.NW, image=scaled_after_tk)

        # 更新畫布的滾動區域
        canvas_before.config(scrollregion=(0, 0, scaled_before.width, scaled_before.height))
        canvas_after.config(scrollregion=(0, 0, scaled_after.width, scaled_after.height))

        # 防止圖片被垃圾回收
        canvas_before.image = scaled_before_tk
        canvas_after.image = scaled_after_tk

    def pan_start(event):
        """開始平移"""
        canvas_before.scan_mark(event.x, event.y)
        canvas_after.scan_mark(event.x, event.y)

    def pan_move(event):
        """執行平移"""
        canvas_before.scan_dragto(event.x, event.y, gain=1)
        canvas_after.scan_dragto(event.x, event.y, gain=1)

    def pan_end(event):
        """平移結束後恢復焦點"""
        root.focus_set()

    def close_window(event):
        """按下 Enter 鍵關閉視窗"""
        root.destroy()

    # 綁定事件
    root.bind_all("<MouseWheel>", zoom)  # 滑鼠滾輪放大/縮小
    root.bind_all("r", lambda event: reset_view())  # 按 R 重置
    root.bind_all("<Return>", close_window)  # 按 Enter 關閉視窗

    # 綁定右鍵平移事件
    canvas_before.bind("<ButtonPress-3>", pan_start)
    canvas_after.bind("<ButtonPress-3>", pan_start)
    canvas_before.bind("<B3-Motion>", pan_move)
    canvas_after.bind("<B3-Motion>", pan_move)
    canvas_before.bind("<ButtonRelease-3>", pan_end)
    canvas_after.bind("<ButtonRelease-3>", pan_end)

    # 啟動主循環
    root.mainloop()


# 主程式部分
if __name__ == "__main__":
    # 設定圖片路徑與輸出路徑
    input_path = "./results/After_Magic_wand.png"
    output_path = "./results/After_Feathering.png" 

    # 執行反鋸齒處理
    before, after = anti_aliasing(input_path, output_path, blur_radius=2)

    # 顯示處理前後的圖片，並支援放大、縮小和平移功能
    show_images_with_gui(before, after)
