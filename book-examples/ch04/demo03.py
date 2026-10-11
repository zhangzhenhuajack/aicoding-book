#!/usr/bin/env python3
"""仓库上下文打包器（本书示例，单文件可独立运行）。

按"渐进式披露"分三级为一次任务组织上下文，并在 token 预算内取舍：
  Level 1 索引（repo map）：每个文件一行摘要，常驻、极短。
  Level 2 相关整文件：按与任务查询的词面相关度排序，整文件纳入。
  Level 3 片段：预算快用尽时，只截取文件里与查询最相关的函数。
核心纪律（正文 4.3 Context Rot）：价值由信噪比决定，不由体积决定——
所以无关文件直接丢弃，预算不足则降级为片段，宁可少给，不稀释注意力。
token 估算用粗略近似：约 4 字符 ≈ 1 token（真实项目请换模型自带分词器）。
"""
import re

# ---- 样例"仓库"：路径 -> 源码（本书构造，真实可跑） ----
REPO = {
    "src/auth/invite.py": (
        "def create_invite(tenant_id, email):\n"
        "    # 为租户生成一张邀请，校验配额与重复\n"
        "    return save_invite(tenant_id, email, _gen_token(tenant_id, email))\n\n"
        "def accept_invite(token):\n"
        "    inv = load_invite(token)\n"
        "    if inv.expired:\n"
        "        raise InviteExpired(token)\n"
        "    return attach_member(inv.tenant_id, inv.email)\n"
    ),
    "src/auth/token.py": (
        "def _gen_token(tenant_id, email):\n"
        "    # HMAC 派生，含租户与邮箱，防跨租户复用\n"
        "    return hmac_sign(f'{tenant_id}:{email}')\n"
    ),
    "src/billing/report.py": (
        "def monthly_report(tenant_id):\n"
        "    # 按月汇总账单，与本任务无关\n"
        "    return summarize(query_usage(tenant_id))\n"
    ),
    "src/ui/theme.py": "DEFAULT_THEME = 'dark'\n# 前端主题常量，与本任务无关\n",
    "docs/invite-spec.md": (
        "# 邀请功能规格\n"
        "- 邀请可过期；过期后 accept 必须报错\n"
        "- 禁止跨租户接受邀请\n"
        "- 同一邮箱重复邀请应幂等\n"
    ),
}


def est_tokens(text):                       # 粗略：约 4 字符 1 token
    return max(1, len(text) // 4)


def summarize(path, src):                   # Level 1：一行摘要
    defs = re.findall(r"^def (\w+)", src, flags=re.M)
    if defs:
        return f"{path}: 定义 {', '.join(defs)}"
    head = re.search(r"^#\s*(.+)$", src, flags=re.M)
    return f"{path}: {head.group(1)}" if head else f"{path}: 杂项"


def score(query, path, src):                # 词面相关度：查询词出现次数
    words = [w for w in re.split(r"\W+", query.lower()) if w]
    hay = (path + "\n" + src).lower()
    return sum(hay.count(w) for w in words)


def extract_snippet(query, src):            # Level 3：取最相关的函数块
    blocks = [b for b in re.split(r"(?=^def )", src, flags=re.M) if b.strip()]
    if not blocks:
        return src.strip()
    return max(blocks, key=lambda b: score(query, "", b)).strip()


def pack(query, budget):
    index, full_files, snippets, used = [], [], [], 0
    for path, src in REPO.items():          # Level 1：索引常驻（必进、极短）
        line = summarize(path, src)
        index.append(line)
        used += est_tokens(line)

    ranked = sorted(((p, s, score(query, p, s)) for p, s in REPO.items()),
                    key=lambda t: t[2], reverse=True)   # 按相关度排序
    for path, src, rel in ranked:
        if rel == 0:
            continue                        # 无关：绝不塞（信噪比纪律）
        cost = est_tokens(src)
        if used + cost <= budget:
            full_files.append(f"# {path}\n{src}")       # Level 2：整文件
            used += cost
        else:                                            # Level 3：降级为片段
            snip = extract_snippet(query, src)
            if used + est_tokens(snip) <= budget:
                snippets.append(f"# {path} (片段)\n{snip}")
                used += est_tokens(snip)
    return index, full_files, snippets, used


def render(query, budget):
    index, full_files, snippets, used = pack(query, budget)
    print(f"########## 预算={budget} token ##########")
    print("==== Level 1 索引（常驻）====")
    print("\n".join(index))
    if full_files:
        print("==== Level 2 相关整文件 ====")
        print("\n".join(full_files))
    if snippets:
        print("==== Level 3 片段（预算不足降级）====")
        print("\n".join(snippets))
    print(f"[统计] 实际用 {used} token / 预算 {budget}；"
          f"整文件 {len(full_files)} 个，片段 {len(snippets)} 个\n")


if __name__ == "__main__":
    q = "租户 邀请 过期 invite tenant expire"
    render(q, 1000)
    render(q, 100)
