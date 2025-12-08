import frappe
from frappe import _
from frappe.utils import add_days, nowdate


def execute(filters=None):
    f = frappe._dict(filters or {})
    columns = [
        {"label": _("Time"), "fieldname": "last_indexed_at", "fieldtype": "Datetime", "width": 160},
        {"label": _("Course"), "fieldname": "course", "fieldtype": "Link", "options": "LMS Course", "width": 180},
        {"label": _("Lesson"), "fieldname": "lesson", "fieldtype": "Link", "options": "Course Lesson", "width": 200},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 90},
        {"label": _("Chunk Count"), "fieldname": "chunk_count", "fieldtype": "Int", "width": 110},
        {"label": _("Embedded Chunks"), "fieldname": "embedded_chunks", "fieldtype": "Int", "width": 130},
        {"label": _("Coverage %"), "fieldname": "coverage", "fieldtype": "Percent", "width": 100},
        {"label": _("Notes"), "fieldname": "notes", "fieldtype": "Small Text", "width": 240},
    ]

    conditions = []
    params = {}
    if f.get("course"):
        conditions.append("course = %(course)s")
        params["course"] = f.course
    if f.get("lesson"):
        conditions.append("lesson = %(lesson)s")
        params["lesson"] = f.lesson
    days = int(f.get("days") or 7)
    if days > 0:
        conditions.append("last_indexed_at >= %(from_date)s")
        params["from_date"] = add_days(nowdate(), -days)
    where = (" where " + " and ".join(conditions)) if conditions else ""

    runs = frappe.db.sql(
        f"""
        select course, lesson, status, chunk_count, last_indexed_at, notes
        from `tabAI Knowledge Index Run`
        {where}
        order by last_indexed_at desc
        limit 500
        """,
        params,
        as_dict=True,
    )
    out = []
    for r in runs:
        totals = frappe.db.sql(
            """
            select count(*) as total,
                   sum(case when coalesce(embedding_model, '') != '' then 1 else 0 end) as embedded
            from `tabAI Knowledge Chunk`
            where course = %(course)s and ( %(lesson)s is null or lesson = %(lesson)s )
            """,
            {"course": r.course, "lesson": r.lesson},
            as_dict=True,
        )
        total_chunks = int((totals[0].total if totals else 0) or 0)
        embedded_chunks = int((totals[0].embedded if totals else 0) or 0)
        coverage = 0
        if total_chunks:
            coverage = round(embedded_chunks * 100.0 / total_chunks, 2)
        out.append(
            {
                "last_indexed_at": r.last_indexed_at,
                "course": r.course,
                "lesson": r.lesson,
                "status": r.status,
                "chunk_count": r.chunk_count,
                "embedded_chunks": embedded_chunks,
                "coverage": coverage,
                "notes": r.notes,
            }
        )

    return columns, out

