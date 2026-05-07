#!/usr/bin/env python3
"""
Parse cached Amazon SP-API Report type values HTML pages and merge a structured
Chinese summary into references/report-requests/types/*.md

HTML 来源：https://developer-docs.amazon.com/sp-api/docs/report-type-values
及其下挂的 report-type-values-* 子页。示例（输出到 references/_spapi_docs_cache/）：

  BASE="https://developer-docs.amazon.com/sp-api/docs"
  for s in report-type-values-amazon-business report-type-values-analytics \\
    report-type-values-b2b-product-opportunities report-type-values-browse-tree \\
    report-type-values-easy-ship report-type-values-fba report-type-values-inventory \\
    report-type-values-invoice-data report-type-values-order report-type-values-payment \\
    report-type-values-performance report-type-values-regulatory-compliance \\
    report-type-values-returns report-type-values-settlement report-type-values-tax; do
    curl -sL "$BASE/$s" -o "references/_spapi_docs_cache/$s.html"
  done

依赖：beautifulsoup4（`pip install beautifulsoup4` 或
`python3 -m pip install --target scripts/_pydeps beautifulsoup4` 后设置 PYTHONPATH）。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "references" / "_spapi_docs_cache"
TYPES = ROOT / "references" / "report-requests" / "types"
BASE_URL = "https://developer-docs.amazon.com/sp-api/docs"
MAIN_URL = f"{BASE_URL}/report-type-values"

SECTION_HEADER_FULL = "## 官方说明（Report type values）"
SECTION_HEADER_INDEX = "## 官方索引（Report type values）"

# `types/*.md` 与 `report-requests/*Report*.md`（GitHub schema 专页）并存时，省略与专页重复的
# 要点 / reportOptions 摘录 / Schema 链接，仅保留索引与权限类字段。
SCHEMA_MD_BY_REPORT_TYPE: dict[str, tuple[str, ...]] = {
    "GET_B2B_PRODUCT_OPPORTUNITIES_NOT_YET_ON_AMAZON": (
        "b2bProductOpportunitiesNotYetOnAmazonReport-2020-11-19.md",
    ),
    "GET_B2B_PRODUCT_OPPORTUNITIES_RECOMMENDED_FOR_YOU": (
        "b2bProductOpportunitiesRecommendedForYouReport-2020-11-19.md",
    ),
    "END_USER_DATA_REPORT": ("endUserDataReport.md",),
    "MARKETPLACE_ASIN_PAGE_VIEW_METRICS": ("marketplaceAsinPageViewMetrics.md",),
    "GET_PROMOTION_PERFORMANCE_REPORT": ("promotionReport.md",),
    "GET_COUPON_PERFORMANCE_REPORT": ("sellerCouponReport.md", "vendorCouponReport.md"),
    "GET_SALES_AND_TRAFFIC_REPORT": ("sellerSalesAndTrafficReport.md",),
    "GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT": ("sellingPartnerMarketBasketAnalysisReport.md",),
    "GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT": ("sellingPartnerRepeatPurchaseReport.md",),
    "GET_BRAND_ANALYTICS_SEARCH_CATALOG_PERFORMANCE_REPORT": (
        "sellingPartnerSearchCatalogPerformanceReport.md",
    ),
    "GET_BRAND_ANALYTICS_SEARCH_QUERY_PERFORMANCE_REPORT": (
        "sellingPartnerSearchQueryPerformanceReport.md",
    ),
    "GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT": ("sellingPartnerSearchTermsReport.md",),
    "GET_VENDOR_FORECASTING_REPORT": ("vendorForecastingReport.md",),
    "GET_VENDOR_INVENTORY_REPORT": ("vendorInventoryReport.md",),
    "GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT": ("vendorNetPureProductMarginReport.md",),
    "GET_VENDOR_REAL_TIME_INVENTORY_REPORT": ("vendorRealTimeInventoryReport.md",),
    "GET_VENDOR_REAL_TIME_SALES_REPORT": ("vendorRealTimeSalesReport.md",),
    "GET_VENDOR_REAL_TIME_TRAFFIC_REPORT": ("vendorRealTimeTrafficReport.md",),
    "GET_VENDOR_SALES_REPORT": ("vendorSalesReport.md",),
    "GET_VENDOR_TRAFFIC_REPORT": ("vendorTrafficReport.md",),
}


def norm_reporttype_strong_text(strong: Tag) -> str:
    return " ".join(strong.get_text(separator=" ", strip=True).split())


def is_report_type_paragraph(p: Tag) -> bool:
    st = p.find("strong")
    if not st:
        return False
    t = norm_reporttype_strong_text(st).lower()
    return t == "reporttype value"


def code_in_report_type_p(p: Tag) -> str | None:
    """Second code in the paragraph is usually the report type enum."""
    codes = p.find_all("code")
    for c in codes:
        t = c.get_text(strip=True)
        if t and t != "reportType":
            return t
    return None


def text_with_links(el: Tag) -> str:
    parts: list[str] = []

    def walk(node):
        if isinstance(node, NavigableString):
            parts.append(str(node))
            return
        if not isinstance(node, Tag):
            return
        if node.name == "a":
            label = node.get_text(strip=True)
            href = node.get("href") or ""
            if href.startswith("/"):
                href = f"https://developer-docs.amazon.com{href}"
            if href and label:
                parts.append(f"[{label}]({href})")
            elif label:
                parts.append(label)
            return
        if node.name in ("button",):
            return
        for ch in node.children:
            walk(ch)

    walk(el)
    s = "".join(parts)
    return " ".join(s.split())


def kv_from_p(p: Tag) -> tuple[str, str] | None:
    st = p.find("strong")
    if not st:
        return None
    key = norm_reporttype_strong_text(st).rstrip(":")
    if key.lower() == "reporttype value":
        return None
    rest = p
    # remove strong from clone by taking tail
    key_len = len(st.get_text())
    raw = text_with_links(p).strip()
    if raw.lower().startswith(key.lower() + ":"):
        val = raw[len(key) + 1 :].strip()
    elif ":" in raw:
        val = raw.split(":", 1)[1].strip()
    else:
        val = raw
    return key, val


def collect_section_nodes(report_p: Tag) -> list[Tag]:
    out: list[Tag] = []
    cur = report_p
    while True:
        sib = cur.next_sibling
        if sib is None:
            break
        if isinstance(sib, NavigableString):
            if str(sib).strip():
                pass
            cur = sib
            continue
        if not isinstance(sib, Tag):
            cur = sib
            continue
        if sib.name == "hr":
            break
        if sib.name == "h2":
            break
        if sib.name == "p" and is_report_type_paragraph(sib):
            break
        if sib.name in ("p", "blockquote", "ul", "ol", "details", "pre"):
            out.append(sib)
        cur = sib
    return out


def prev_restricted(report_p: Tag) -> bool:
    cur = report_p
    while cur is not None:
        cur = cur.find_previous_sibling()
        if cur is None:
            break
        if isinstance(cur, Tag) and cur.name == "h3":
            break
        if isinstance(cur, Tag) and cur.name == "blockquote":
            if "restricted" in cur.get_text().lower():
                return True
    return False


def section_h3_anchor(report_p: Tag) -> tuple[str, str]:
    h3 = report_p.find_previous("h3")
    if not h3:
        return "", ""
    title = h3.get_text(strip=True)
    aid = ""
    wa = h3.find(class_="waypoint")
    if wa and wa.get("id"):
        aid = wa["id"]
    return title, aid


def summarize_nodes(nodes: list[Tag], include_details_attrs: bool = False) -> tuple[dict[str, str], list[str], list[str]]:
    kv: dict[str, str] = {}
    paras: list[str] = []
    options: list[str] = []
    last_p_plain = ""
    for el in nodes:
        if el.name == "p":
            pair = kv_from_p(el)
            if pair:
                k, v = pair
                kv[k] = v
            else:
                t = text_with_links(el).strip()
                if t:
                    paras.append(t)
            last_p_plain = el.get_text(separator=" ", strip=True)
        elif el.name == "blockquote":
            t = text_with_links(el).strip()
            if t and "restricted" not in t.lower()[:80]:
                paras.append(t)
        elif el.name in ("ul", "ol"):
            opt_ctx = "reportOptions" in last_p_plain or "report options" in last_p_plain.lower()
            for li in el.find_all("li", recursive=False):
                line = text_with_links(li).strip()
                if not line:
                    continue
                if opt_ctx:
                    options.append(line)
        elif el.name == "details" and include_details_attrs:
            paras.append("(字段/属性列表见官方页面 expandable 区块。)")
    return kv, paras, options


def build_markdown_block(
    slug: str,
    page_title: str,
    h3_title: str,
    anchor: str,
    rtype: str,
    restricted: bool,
    kv: dict[str, str],
    paras: list[str],
    options: list[str],
) -> str:
    doc_url = f"{BASE_URL}/{slug}"
    if anchor:
        doc_url = f"{doc_url}#{anchor}"

    sub_label = page_title or slug
    lines: list[str] = [
        f"以下内容整理自官方 [Report type values]({MAIN_URL}) 子页 "
        f"[{sub_label}]({doc_url})（章节：**{h3_title or rtype}**）。"
        f"**与专页其它段落冲突时以官方英文文档为准。**",
        "",
    ]
    role_txt = (kv.get("Role") or "").lower()
    if restricted:
        lines.append("- **受限报告**：是（相邻 Note 标明 restricted：下载结果需 RDT，参见官方 Tokens API）")
    elif "restricted" in role_txt:
        lines.append(
            "- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准"
        )
    else:
        lines.append("- **受限报告**：按当前小节文本为否（仍以官方为准）")

    order_keys = [
        "Role",
        "Order Fulfillment Channel",
        "Availability",
        "Marketplace availability",
        "Marketplaces",
        "Requested/scheduled",
        "Report output type",
        "Selling Partner",
        "Granularity",
    ]
    for k in order_keys:
        if k in kv and str(kv[k]).strip():
            lines.append(f"- **{k}**：{kv[k]}")

    for k, v in sorted(kv.items()):
        if k in order_keys or k in ("reportType value",):
            continue
        if not str(v).strip():
            continue
        lines.append(f"- **{k}**：{v}")

    # Descriptive sentences (dedupe, cap)
    seen: set[str] = set()
    kept: list[str] = []
    for p in paras:
        p = p.strip()
        if len(p) < 3 or p in seen:
            continue
        if "Select to expand" in p:
            continue
        seen.add(p)
        kept.append(p)
        if len(kept) >= 5:
            break
    if kept:
        lines.append(f"- **要点**：{' '.join(kept)}")

    if options:
        lines.append("- **reportOptions（摘录）**：")
        for o in options[:12]:
            lines.append(f"  - {o}")
        if len(options) > 12:
            lines.append(f"  - …（另有 {len(options) - 12} 项，见官方）")

    lines.append("")
    lines.append(f"- **官方直达**：<{doc_url}>")

    return "\n".join(lines)


def build_slim_index_block(
    slug: str,
    page_title: str,
    h3_title: str,
    anchor: str,
    rtype: str,
    restricted: bool,
    kv: dict[str, str],
    schema_files: tuple[str, ...],
) -> str:
    doc_url = f"{BASE_URL}/{slug}"
    if anchor:
        doc_url = f"{doc_url}#{anchor}"
    sub_label = page_title or slug
    link_md = "、".join(f"[`{fn}`](../{fn})" for fn in schema_files)
    lines: list[str] = [
        f"- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：{link_md}",
        f"- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**："
        f"[{sub_label}]({doc_url})（章节：**{h3_title or rtype}**）",
        "",
    ]
    role_txt = (kv.get("Role") or "").lower()
    if restricted:
        lines.append("- **受限报告**：是（相邻 Note 标明 restricted：下载结果需 RDT，参见官方 Tokens API）")
    elif "restricted" in role_txt:
        lines.append(
            "- **受限报告**：未在相邻 Note 中写明，但 **Role** 含 *Restricted*；**仍可能**需 RDT/额外审核，以官方为准"
        )
    else:
        lines.append("- **受限报告**：按当前小节文本为否（仍以官方为准）")

    order_keys = [
        "Role",
        "Order Fulfillment Channel",
        "Availability",
        "Marketplace availability",
        "Marketplaces",
        "Requested/scheduled",
        "Report output type",
        "Selling Partner",
        "Granularity",
    ]
    for k in order_keys:
        if k in kv and str(kv[k]).strip():
            lines.append(f"- **{k}**：{kv[k]}")

    lines.append("")
    lines.append(f"- **官方直达**：<{doc_url}>")
    return "\n".join(lines)


def parse_html_file(path: Path) -> dict[str, dict]:
    slug = path.stem  # report-type-values-order
    text = path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(text, "html.parser")
    candidates = soup.select('[data-testid="RDMD"]')
    root = None
    if candidates:
        root = max(candidates, key=lambda t: len(t.get_text()))
    if not root or len(root.get_text()) < 500:
        root = soup.select_one("article") or soup.select_one("main")
    if not root:
        return {}

    raw_title = (soup.title and soup.title.string) or ""
    page_title = raw_title.replace("| Selling Partner API", "").strip()

    out: dict[str, dict] = {}
    for p in root.find_all("p"):
        if not is_report_type_paragraph(p):
            continue
        rtype = code_in_report_type_p(p)
        if not rtype:
            continue
        h3_title, anchor = section_h3_anchor(p)
        nodes = collect_section_nodes(p)
        kv, paras, options = summarize_nodes(nodes)
        out[rtype] = {
            "slug": slug,
            "page_title": page_title,
            "h3_title": h3_title,
            "anchor": anchor,
            "restricted": prev_restricted(p),
            "kv": kv,
            "paras": paras,
            "options": options,
        }
    return out


def report_type_from_md(path: Path) -> str | None:
    line = path.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    m = re.match(r"^# `([^`]+)`\s*$", line)
    return m.group(1) if m else None


SCHEMA_SECTION_SLIM = """## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。

"""


def dedupe_schema_follow_section(md_path: Path) -> None:
    """已存在 GitHub schema 专页时，去掉 types 中与「官方索引」重复的 Schema 说明段落。"""
    text = md_path.read_text(encoding="utf-8", errors="replace")
    pat = re.compile(
        r"## 官方 JSON Schema 与请求/结果说明\n\n[\s\S]*?(?=\n## CreateReport)",
        re.MULTILINE,
    )
    if not pat.search(text):
        return
    text = pat.sub(SCHEMA_SECTION_SLIM, text, count=1)
    md_path.write_text(text, encoding="utf-8")


def merge_into_md(md_path: Path, block: str, section_header: str) -> bool:
    text = md_path.read_text(encoding="utf-8", errors="replace")
    section = section_header + "\n\n" + block.strip() + "\n\n"
    pat = re.compile(
        r"## 官方(?:说明|索引)（Report type values）\n[\s\S]*?(?=\n## |\Z)",
        re.MULTILINE,
    )
    if pat.search(text):
        text = pat.sub(section.rstrip() + "\n\n", text, count=1)
    else:
        m = re.search(r"\n(## 官方)", text)
        if m:
            text = text[: m.start()] + "\n" + section + text[m.start() + 1 :]
        else:
            # Fallback: after first blockquote block
            lines = text.splitlines()
            insert_at = 0
            for i, ln in enumerate(lines):
                if ln.startswith("## "):
                    insert_at = i
                    break
            if insert_at == 0:
                text = text.rstrip() + "\n\n" + section
            else:
                text = "\n".join(lines[:insert_at]) + "\n\n" + section + "\n".join(lines[insert_at:]) + "\n"
    md_path.write_text(text, encoding="utf-8")
    return True


def _richness(meta: dict) -> int:
    return len(meta["kv"]) * 2 + len(meta["paras"]) + len(" ".join(meta["options"])) // 80


def main() -> int:
    all_meta: dict[str, dict] = {}
    for html in sorted(CACHE.glob("report-type-values-*.html")):
        merged = parse_html_file(html)
        for k, v in merged.items():
            if k not in all_meta:
                all_meta[k] = v
            elif _richness(v) > _richness(all_meta[k]):
                sys.stderr.write(f"note: duplicate {k}: prefer {html.name} (richer section)\n")
                all_meta[k] = v

    updated = 0
    missing: list[str] = []
    for md in sorted(TYPES.glob("*.md")):
        if md.name == "README.md":
            continue
        rtype = report_type_from_md(md)
        if not rtype:
            continue
        meta = all_meta.get(rtype)
        if not meta:
            missing.append(rtype)
            continue
        schema_docs = SCHEMA_MD_BY_REPORT_TYPE.get(rtype)
        if schema_docs:
            block = build_slim_index_block(
                slug=meta["slug"],
                page_title=meta["page_title"],
                h3_title=meta["h3_title"],
                anchor=meta["anchor"],
                rtype=rtype,
                restricted=meta["restricted"],
                kv=meta["kv"],
                schema_files=schema_docs,
            )
            merge_into_md(md, block, SECTION_HEADER_INDEX)
            dedupe_schema_follow_section(md)
        else:
            block = build_markdown_block(
                slug=meta["slug"],
                page_title=meta["page_title"],
                h3_title=meta["h3_title"],
                anchor=meta["anchor"],
                rtype=rtype,
                restricted=meta["restricted"],
                kv=meta["kv"],
                paras=meta["paras"],
                options=meta["options"],
            )
            merge_into_md(md, block, SECTION_HEADER_FULL)
        updated += 1

    print(f"updated {updated} type pages; parsed {len(all_meta)} report types from cache")
    if missing:
        print(f"missing in cache parse: {len(missing)}")
        for x in missing[:30]:
            print(" ", x)
        if len(missing) > 30:
            print(" ...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
