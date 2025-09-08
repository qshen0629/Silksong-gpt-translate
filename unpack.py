import os
import sys
import argparse
from typing import Optional
import UnityPy
from UnityPy.classes import Font


def export_textassets(src_path: str, out_dir: str) -> None:
    if not os.path.exists(src_path):
        print(f"找不到资源文件: {src_path}")
        sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)

    env = UnityPy.load(src_path)

    total_objects = 0
    exported_files = 0
    for obj in env.objects:
        total_objects += 1
        if obj.type.name == "TextAsset":
            data = obj.read()
            filename = f"{data.m_Name}.txt"
            path = os.path.join(out_dir, filename)
            with open(path, "wb") as f:
                f.write(data.m_Script.encode("utf-8", "surrogateescape"))
            exported_files += 1
            print(f"导出: {filename}")

    print(f"完成。对象总数: {total_objects}，导出 TextAsset: {exported_files}，输出目录: {out_dir}")


def import_textassets(src_path: str, in_dir: str, output: Optional[str], in_place: bool, backup: bool) -> None:
    if not os.path.exists(src_path):
        print(f"找不到资源文件: {src_path}")
        sys.exit(1)
    if not os.path.isdir(in_dir):
        print(f"找不到输入目录: {in_dir}")
        sys.exit(1)

    if in_place and output:
        print("不能同时使用 --in-place 和 --output")
        sys.exit(1)

    # 目标输出路径
    if in_place:
        dst_path = src_path
    else:
        if output:
            dst_path = output
        else:
            base_dir = os.path.dirname(src_path)
            dst_path = os.path.join(base_dir, "resources_patched.assets")

    # 备份
    if in_place and backup and os.path.exists(src_path):
        bak_path = src_path + ".bak"
        if not os.path.exists(bak_path):
            with open(src_path, "rb") as rf, open(bak_path, "wb") as wf:
                wf.write(rf.read())
            print(f"已备份为: {bak_path}")

    env = UnityPy.load(src_path)

    modified = 0
    total_textassets = 0
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        total_textassets += 1
        data = obj.read()
        filename = f"{data.m_Name}.txt"
        candidate = os.path.join(in_dir, filename)
        if os.path.exists(candidate):
            # 读取新文本并写入到 TextAsset（保留不可解码字节）
            new_text = open(candidate, "r", encoding="utf-8", errors="surrogateescape").read()
            data.m_Script = new_text
            # 提交更改到对象
            data.save()
            modified += 1
            print(f"替换: {filename}")

    # 保存到目标文件
    with open(dst_path, "wb") as f:
        f.write(env.file.save())

    print(
        f"完成。TextAsset 总数: {total_textassets}，替换: {modified}，输出: {dst_path}"
    )


def main() -> None:
    p = argparse.ArgumentParser(description="导出/导入 Unity TextAsset 文本")
    p.add_argument("--mode", choices=["export", "import"], default="export")
    p.add_argument("--src", default="assets/resources.assets", help="资源文件路径")
    p.add_argument("--out-dir", default="assets_unpacked", help="导出目录（mode=export）")
    p.add_argument("--in-dir", default="new_ZH", help="导入目录（mode=import）")
    p.add_argument("--output", help="导入后的输出文件（默认 resources_patched.assets）")
    p.add_argument("--in-place", action="store_true", help="直接覆盖源资源文件")
    p.add_argument("--backup", action="store_true", help="in-place 时先备份 .bak")

    args = p.parse_args()

    if args.mode == "export":
        export_textassets(src_path=args.src, out_dir=args.out_dir)
    else:
        import_textassets(
            src_path=args.src,
            in_dir=args.in_dir,
            output=args.output,
            in_place=args.in_place,
            backup=args.backup,
        )


if __name__ == "__main__":
    main()
