"use strict";
let boot,
  bank,
  state,
  day = 1,
  activeCard = null,
  cardSession = null,
  exam = null,
  examTimer = null;
const main = document.querySelector("#main");
const pendingSaves = new Map();
function scheduleSave(key, job) {
  const previous = pendingSaves.get(key);
  if (previous) clearTimeout(previous.timer);
  const entry = {
    promise: null,
    timer: null,
    job: async () => {
      if (previous?.promise) await previous.promise;
      await job();
    },
  };
  entry.timer = setTimeout(
    () => performSave(key, entry).catch((e) => toast(e.message)),
    400,
  );
  pendingSaves.set(key, entry);
}
function performSave(key, entry) {
  if (entry.promise) return entry.promise;
  clearTimeout(entry.timer);
  entry.promise = entry
    .job()
    .then(() => {
      if (pendingSaves.get(key) === entry) pendingSaves.delete(key);
    })
    .catch((e) => {
      entry.promise = null;
      throw e;
    });
  return entry.promise;
}
async function flushSaves() {
  await Promise.all(
    [...pendingSaves].map(([key, entry]) => performSave(key, entry)),
  );
}

const esc = (v) =>
  String(v ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const q = (id) => bank.questions.find((x) => x.question_id === id);
const card = (id) => bank.cards.find((x) => x.id === id);
const short = (id) => id.replace("TN1-", "");
const dateText = (d) =>
  new Date(d + "T12:00:00").toLocaleDateString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
  });
const due = () =>
  Object.entries(state.progress)
    .filter(([, p]) => p.due <= boot.today)
    .map(([id]) => id);
const weak = () =>
  Object.entries(state.progress)
    .filter(([, p]) => p.score < 85 || !p.mastered)
    .map(([id]) => id);
const on = (selector, event, fn) =>
  document
    .querySelectorAll(selector)
    .forEach((el) => el.addEventListener(event, fn));
function toast(message) {
  const t = document.querySelector("#toast");
  t.textContent = message;
  t.classList.add("visible");
  clearTimeout(t.timeout);
  t.timeout = setTimeout(() => t.classList.remove("visible"), 4500);
}
async function api(path, data) {
  const response = await fetch(
    "/api/" + path,
    data === undefined
      ? {}
      : {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        },
  );
  const result = await response.json();
  if (!response.ok) throw Error(result.error || "Không lưu được dữ liệu.");
  return result;
}
function guarded(fn) {
  return async (event) => {
    try {
      await fn(event);
    } catch (e) {
      toast(e.message);
    }
  };
}
async function refresh() {
  boot = await api("bootstrap");
  bank = boot.bank;
  state = boot.state;
  document.querySelector("#due-count").textContent = due().length;
}
const src = (kind, page, label) =>
  `<a href="/sources/${kind}.pdf#page=${page}" target="_blank" rel="noopener">${esc(label || `${kind === "slide" ? "Slide" : "Đề cương"} · PDF ${page}`)} ↗</a>`;
const heading = (eyebrow, title, description) =>
  `<div class="eyebrow">${eyebrow}</div><h1>${title}</h1><p class="muted">${description}</p>`;
function cardRows(ids) {
  return ids
    .map((id) => {
      const c = card(id),
        p = state.progress[id];
      return `<div class="qrow"><span class="number">${short(id).slice(1)}</span><div class="qtext"><strong>${esc(c?.title || q(id)?.original_text.split("\n")[0])}</strong><small>${esc(q(id)?.section_id)} · ${src("outline", q(id)?.pdf_page)}${p ? ` · Ôn ${dateText(p.due)}` : ""}</small></div><span class="pill ${p?.mastered ? "green" : c ? "" : "amber"}">${p?.mastered ? "Nhớ độc lập" : c ? (p ? `${p.score}% · tự đối chiếu` : "Chưa luyện") : "Chờ đáp án kiểm chứng"}</span><a class="button small" href="#card/${id}/${day}">${c ? "Tự trả lời" : "Xem câu gốc"}</a></div>`;
    })
    .join("");
}
function taskHtml(plan) {
  const saved = state.settings.tasks || {};
  return plan.tasks
    .map(
      (t, i) =>
        `<label class="task ${saved[`${plan.day}-${i}`] ? "checked" : ""}"><input type="checkbox" data-task="${plan.day}-${i}" ${saved[`${plan.day}-${i}`] ? "checked" : ""}><span>${esc(t.title)}</span><small>${t.minutes} phút</small></label>`,
    )
    .join("");
}
function dayView(n) {
  day = Math.max(1, Math.min(51, Number(n) || 1));
  const p = bank.plan[day - 1],
    ready = p.card_ids.filter((id) => card(id)),
    graded = new Set(
      state.attempts
        .filter((a) => a.day === day && a.graded)
        .map((a) => a.card_id),
    );
  const learned = ready.filter((id) => graded.has(id)).length;
  const next = ready.find((id) => !graded.has(id)) || ready[0];
  const effective = (state.settings.schedule || {})[day] || p.date;
  main.innerHTML = `<div class="row calendar-info"><span>TUẦN ${p.week} · NGÀY ${day}/51 · ${dateText(effective)}/2026${effective !== p.date ? " · Lịch đã điều chỉnh" : ""}</span><div class="actions">${day > 1 ? `<a href="#day/${day - 1}">← Hôm trước</a>` : ""}${day < 51 ? `<a href="#day/${day + 1}">Hôm sau →</a>` : ""}</div></div>
<section class="hero"><div><div class="eyebrow">MỖI LẦN NHỚ LẠI LÀ MỘT LẦN HỌC</div><h1>${esc(p.title)}</h1><p>${day === 1 ? "Bắt đầu bằng việc tự nhớ. Viết điều bạn biết, đối chiếu từng ý, rồi để lịch ôn đưa những câu chưa chắc trở lại." : "Một phiên học rõ mục tiêu: tự trả lời trước, thực hành, kiểm tra lại và ghi điều cần sửa."}</p><div class="actions">${next ? `<a class="button primary" href="#card/${next}/${day}">${learned ? "Tiếp tục phiên học" : "Bắt đầu tự trả lời"} →</a>` : `<a class="button primary" href="#bank">Mở câu hỏi của ngày</a>`}<a class="button" href="${day === 1 ? "#exams" : "#review"}">${day === 1 ? "Kiểm tra đầu vào" : "Ôn câu đến hạn"}</a></div></div><div class="hero-stat"><strong>${learned}<span> / ${ready.length}</span></strong><span>CÂU ĐÃ LÀM & ĐỐI CHIẾU</span><div class="progress-bar" style="--progress:${ready.length ? (learned / ready.length) * 100 : 0}%"><i></i></div></div></section>
<div class="stats"><div class="stat"><span>Thời gian dự kiến</span><strong>${p.minutes} <small>phút</small></strong></div><div class="stat"><span>Đến hạn hôm nay</span><strong>${due().length} <small>câu</small></strong></div><div class="stat"><span>Cần củng cố</span><strong>${weak().length} <small>câu</small></strong></div><div class="stat"><span>Nhớ độc lập ổn định</span><strong>${Object.values(state.progress).filter((x) => x.mastered).length} <small>/ ${bank.reviewed}</small></strong></div></div>
<div class="grid"><section class="panel"><div class="row"><h2>Câu hỏi của phiên học</h2><span class="pill green">${ready.length}/${p.card_ids.length} đáp án đã đối chiếu</span></div>${cardRows(p.card_ids)}${ready.length < p.card_ids.length ? '<div class="note">Câu hỏi giữ nguyên theo đề cương. Một số đáp án của ngày này chưa được kiểm chứng; hiện chỉ có thể đọc câu gốc, không được tính là đã học xong.</div>' : ""}</section><div><section class="panel"><h2>Nhịp học hôm nay</h2><p class="hint-text">Đánh dấu sau khi thực sự làm xong nhiệm vụ. Việc mở trang không được tính hoàn thành.</p>${taskHtml(p)}</section><section class="panel soft"><div class="eyebrow">THỰC HÀNH CÓ PHẢN HỒI</div><h3>${day >= 5 && day <= 7 ? "Tái hiện giao thức xác thực" : "Chuyển từ nhớ sang hiểu"}</h3><p class="hint-text">Tô sáng từng bước, thử điền thông điệp còn thiếu hoặc kiểm tra một phép tính.</p><div class="actions"><a class="button small" href="#diagrams">Mở sơ đồ ⇄</a><a class="button small" href="#math">Bảng toán ∑</a></div></section></div></div>
<h2>Tuần đầu · 12–18 tháng 10</h2><div class="day-strip">${bank.plan
    .slice(0, 7)
    .map(
      (d) =>
        `<a href="#day/${d.day}" class="day-tile ${d.day === day ? "selected" : ""}"><span>${dateText((state.settings.schedule || {})[d.day] || d.date)}</span><strong>${String(d.day).padStart(2, "0")}</strong><span>${esc(d.title)}</span><em>${d.card_ids.length} câu</em></a>`,
    )
    .join("")}</div>`;
  on(
    "[data-task]",
    "change",
    guarded(async (e) => {
      const tasks = {
        ...state.settings.tasks,
        [e.target.dataset.task]: e.target.checked,
      };
      await api("settings", { key: "tasks", value: tasks });
      state.settings.tasks = tasks;
      e.target.closest("label").classList.toggle("checked", e.target.checked);
      toast("Đã lưu nhiệm vụ.");
    }),
  );
}
function planView() {
  main.innerHTML =
    heading(
      "LỘ TRÌNH CÓ THỂ ĐIỀU CHỈNH",
      "51 ngày, từng phiên học rõ ràng",
      "12/10–01/12/2026. Câu đến hạn được thêm vào phiên học; lịch có thể dời mà vẫn giữ lịch sử bài làm.",
    ) +
    `<div class="info">Tuần 1 có ${bank.reviewed} câu với đáp án và rubric đã đối chiếu. Lộ trình các tuần sau đã có câu hỏi nguyên văn; cần bổ sung đáp án kiểm chứng trước khi nghiệm thu toàn bộ 51 ngày.</div>` +
    Array.from(
      { length: 8 },
      (_, i) =>
        `<h2 class="week-heading">Tuần ${i + 1}</h2><div class="day-strip">${bank.plan
          .filter((p) => p.week === i + 1)
          .map((p) => {
            const ready = p.card_ids.filter((id) => card(id)).length;
            return `<a href="#day/${p.day}" class="day-tile"><span>${dateText((state.settings.schedule || {})[p.day] || p.date)} · ${p.minutes} phút</span><strong>${String(p.day).padStart(2, "0")}</strong><span>${esc(p.title)}</span><em>${ready}/${p.card_ids.length} đáp án sẵn sàng</em></a>`;
          })
          .join("")}</div>`,
    ).join("");
}
function sourcePanel(c) {
  return `<div class="source-links">${c.sources.map((s) => src("slide", s.page)).join("")}</div>${c.derivations ? `<div class="info"><b>DERIVED · Vận dụng:</b> ${esc(c.derivations)}</div>` : ""}${c.note ? `<div class="note">${esc(c.note)}</div>` : ""}<details><summary>Đoạn chứng cứ trong tài liệu</summary><p class="hint-text">Trang PDF (đếm từ 1), đã đối chiếu hình. SHA nguồn ${bank.sha.slice(0, 16)}…</p>${c.sources.map((s) => `<details><summary>PDF ${s.page} · SLIDE_GROUNDED</summary><pre class="excerpt">${esc(s.excerpt)}</pre></details>`).join("")}</details>`;
}
function rubricHtml(c, prefix = "r") {
  return c.rubric
    .map(
      (r) =>
        `<label><input type="checkbox" name="${prefix}" value="${r.id}"><span>${esc(r.label)}${r.essential ? " <em>Ý cốt lõi</em>" : ""}</span></label>`,
    )
    .join("");
}
function cardView(id, n) {
  day = Number(n) || 1;
  activeCard = id;
  cardSession = null;
  const c = card(id),
    question = q(id);
  if (!question) return (main.innerHTML = "<p>Không có câu hỏi này.</p>");
  if (!c) {
    main.innerHTML = `<div class="narrow">${heading("ĐỀ CƯƠNG NGUYÊN VĂN", short(id), "Giữ nguyên phạm vi và dữ kiện của tài liệu gốc.")}<section class="panel"><div class="long-question">${esc(question.original_text)}</div><div class="source-links">${src("outline", question.pdf_page)}</div><div class="note">AWAITING_REVIEW · Chưa có đáp án tự luận đầy đủ được kiểm chứng. Có thể ghi nháp; nháp không được tính là thành thạo.</div>${{ "TN1-Q037": "math/rsa", "TN1-Q046": "math/elgamal", "TN1-Q048": "math/ecc", "TN1-Q050": "math/dh", "TN1-Q051": "math/ecdh", "TN1-Q028": "code/TN1-Q028", "TN1-Q029": "code/TN1-Q029" }[id] ? `<a class="button primary" style="margin-bottom:20px" href="#${{ "TN1-Q037": "math/rsa", "TN1-Q046": "math/elgamal", "TN1-Q048": "math/ecc", "TN1-Q050": "math/dh", "TN1-Q051": "math/ecdh", "TN1-Q028": "code/TN1-Q028", "TN1-Q029": "code/TN1-Q029" }[id]}">Mở bài thực hành hỗ trợ một phần →</a>` : ""}<textarea id="answer" placeholder="Ghi lời giải hoặc điều cần hỏi…">${esc(state.drafts[id] || "")}</textarea><p class="hint-text" id="save-status">Bản nháp lưu trên máy.</p></section></div>`;
    bindDraft(id);
    return;
  }
  const pending = state.attempts.find((a) => a.card_id === id && !a.graded);
  main.innerHTML = `<div class="narrow"><div class="row"><a href="#day/${day}">← Về phiên ngày ${day}</a><span class="hint-text">Câu hỏi trước · Đáp án sau</span></div><section class="panel" style="margin-top:22px"><div class="card-top"><span class="pill green">${short(id)}</span><span class="pill">${esc(c.topic)}</span><span class="pill">${c.status === "SLIDE_GROUNDED" ? "Căn cứ slide" : "Căn cứ slide + vận dụng"}</span></div><h1>${esc(c.title)}</h1><div class="question">${esc(c.question)}</div>${src("outline", c.outline_page)}${[9, 10, 11].includes(Number(id.slice(-3))) ? `<details><summary>Xem sơ đồ đề gốc (PDF ${id === "TN1-Q011" ? 3 : 2})</summary><img src="/figures/outline-${id === "TN1-Q011" ? 3 : 2}.png" style="width:100%;height:auto" alt="Trang đề gốc chứa sơ đồ xác thực"></details>` : ""}<label class="field" for="answer">Câu trả lời của bạn</label><textarea id="answer" rows="7" placeholder="Thử nhớ lại trước khi dùng gợi ý. Nêu định nghĩa, các ý chính và ví dụ theo yêu cầu.">${esc(state.drafts[id] || pending?.answer || "")}</textarea><div class="split-label"><span id="save-status">Tự lưu bản nháp.</span><span>Tự luận · Không chấm bằng từ khóa</span></div><div id="hints"></div><div class="actions" style="margin-top:20px"><button class="primary" id="reveal">Nộp câu trả lời & đối chiếu →</button><button id="hint-btn">Gợi ý từng cấp</button>${pending ? '<button id="resume">Tiếp tục chấm bài đã nộp</button>' : ""}</div></section><div id="feedback"></div></div>`;
  cardSession = { hints: 0, id };
  bindDraft(id);
  on("#hint-btn", "click", () => {
    if (cardSession.hints >= c.hints.length) return;
    document
      .querySelector("#hints")
      .insertAdjacentHTML(
        "beforeend",
        `<div class="hint"><b>Gợi ý ${cardSession.hints + 1}:</b> ${esc(c.hints[cardSession.hints++])}</div>`,
      );
    document.querySelector("#hint-btn").disabled =
      cardSession.hints >= c.hints.length;
  });
  on(
    "#reveal",
    "click",
    guarded(async () => {
      const result = await api("submit", {
        card_id: id,
        day,
        answer: document.querySelector("#answer").value,
        hints: cardSession.hints,
      });
      showFeedback(result);
    }),
  );
  on(
    "#resume",
    "click",
    guarded(async () =>
      showFeedback(await api("resume", { attempt_id: pending.id })),
    ),
  );
}
function bindDraft(key) {
  on("#answer", "input", () => {
    const val = document.querySelector("#answer").value;
    state.drafts[key] = val;
    const status = document.querySelector("#save-status");
    status.textContent = "Đang lưu…";
    scheduleSave("draft-" + key, async () => {
      await api("draft", { key, answer: val });
      if (document.querySelector("#save-status"))
        document.querySelector("#save-status").textContent = "Đã lưu trên máy.";
    });
  });
}
function showFeedback(result) {
  const c = result.card;
  cardSession = { ...cardSession, attempt_id: result.attempt_id };
  document.querySelector("#reveal").disabled = true;
  document.querySelector("#hint-btn").disabled = true;
  document.querySelector("#answer").readOnly = true;
  if (document.querySelector("#resume"))
    document.querySelector("#resume").disabled = true;
  document.querySelector("#feedback").innerHTML =
    `<section class="panel"><div class="eyebrow">ĐỐI CHIẾU TỪNG Ý</div><h2>Đáp án có căn cứ</h2><p class="answer">${esc(c.answer)}</p>${sourcePanel(c)}</section><section class="panel"><h2>Tự chấm theo rubric</h2><p class="hint-text">Chỉ đánh dấu ý đã có trong bài bạn vừa nộp. Đây là tự đối chiếu; ứng dụng không giả lập giám khảo hiểu ngữ nghĩa. Đạt cần ≥85%, đủ ý cốt lõi và không có sai kiến thức trọng yếu.</p><div class="rubric">${rubricHtml(c)}</div><label class="task"><input id="critical" type="checkbox"><span>Tôi có sai kiến thức cốt lõi, cần học lại</span></label><label class="field" for="confidence">Mức tự tin khi trả lời</label><select id="confidence"><option value="1">1 · Đoán hoặc nhớ không chắc</option><option value="2" selected>2 · Nhớ tương đối chắc</option><option value="3">3 · Giải thích được bằng lời riêng</option></select><label class="field" for="error-note">Ý thiếu hoặc điều cần sửa</label><textarea id="error-note" rows="2" style="min-height:80px" placeholder="Ghi cụ thể để lần ôn tới sửa đúng chỗ."></textarea><div class="actions" style="margin-top:20px"><button id="grade" class="primary">Lưu đánh giá & lên lịch ôn</button></div><div id="grade-result"></div></section>`;
  document
    .querySelector("#feedback")
    .scrollIntoView({ behavior: "smooth", block: "start" });
  on(
    "#grade",
    "click",
    guarded(async () => {
      const r = await api("grade", {
        attempt_id: result.attempt_id,
        checks: [...document.querySelectorAll("input[name=r]:checked")].map(
          (el) => el.value,
        ),
        confidence: Number(document.querySelector("#confidence").value),
        critical_error: document.querySelector("#critical").checked,
        error: document.querySelector("#error-note").value,
      });
      document.querySelector("#grade").disabled = true;
      await refresh();
      document.querySelector("#grade-result").innerHTML =
        `<div class="${r.passed ? "success" : "error-box"}" style="margin-top:18px"><b>${r.score}% · ${r.passed ? "Đủ ý theo tự đối chiếu" : "Cần bổ sung"}</b><br>Ôn lại: ${dateText(r.due)}/2026. ${r.independent ? "Đã ghi một lần nhớ độc lập." : "Lần này có gợi ý, sai hoặc chưa chắc; chưa tính nhớ độc lập."}${r.mastered ? " Hai lần liên tiếp đã nhớ độc lập." : ""}${r.missing.length ? `<ul>${r.missing.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : ""}</div><div class="actions" style="margin-top:18px"><a class="button primary" href="#card/${nextCard(c.id)}/${day}">Câu tiếp theo →</a><a class="button" href="#day/${day}">Về phiên học</a></div>`;
      toast("Đã lưu bài làm và ngày ôn lại.");
    }),
  );
}
function nextCard(id) {
  const ids = bank.plan[day - 1].card_ids.filter((id) => card(id)),
    i = ids.indexOf(id);
  return ids[(i + 1) % ids.length] || bank.cards[0].id;
}
function reviewView() {
  const errors = state.attempts.filter(
    (a) => a.graded && (a.error || a.passed === 0),
  );
  const practiceErrors = state.practices
    .map((p) => ({ ...p, data: JSON.parse(p.payload) }))
    .filter((p) => p.data.correct === false || p.data.located === false);
  main.innerHTML =
    heading(
      "LẶP LẠI NGẮT QUÃNG",
      "Ôn câu đến hạn, sửa đúng chỗ",
      "Lịch +1, +3, +7, +14, +30 ngày. Sai, dùng gợi ý hoặc thiếu tự tin sẽ ôn lại sau 1 ngày. Hai lần nhớ độc lập liên tiếp mới được ghi nhận ổn định.",
    ) +
    `<div class="grid"><div><section class="panel"><h2>Đến hạn · ${dateText(boot.today)}/2026</h2>${due().length ? cardRows(due()) : '<div class="empty">Chưa có câu đến hạn. Hãy học phiên đầu hoặc luyện lại một câu chưa chắc.</div>'}</section><section class="panel"><h2>Cần củng cố</h2>${weak().length ? cardRows(weak()) : '<div class="empty">Sổ này sẽ xuất hiện sau khi bạn nộp và đối chiếu bài đầu tiên.</div>'}</section></div><section class="panel"><h2>Sổ câu sai & ý thiếu</h2>${
      errors.length
        ? errors
            .slice(0, 30)
            .map(
              (a) =>
                `<details><summary>${short(a.card_id)} · ${a.score}% · ${esc(card(a.card_id)?.title)}</summary><p style="margin-top:12px">${esc(a.error || "Sai kiến thức trọng yếu.")}</p><details><summary>Xem bài đã viết</summary><p style="white-space:pre-wrap">${esc(a.answer)}</p></details><a href="#card/${a.card_id}/${day}">Tự trả lời lại →</a></details>`,
            )
            .join("")
        : '<p class="muted">Những ý bạn bỏ sót sẽ được giữ lại ở đây.</p>'
    }</section></div><section class="panel"><h2>Bài thực hành cần làm lại</h2>${
      practiceErrors.length
        ? practiceErrors
            .slice(0, 25)
            .map(
              (p) =>
                `<div class="qrow"><div class="qtext"><strong>${esc(p.data.question_id)} · ${esc(p.kind)}</strong><small>Đã trả lời: ${esc(p.data.answer)}${p.data.expected ? " · Kết quả: " + esc(p.data.expected) : ""}</small></div><a class="button small" href="#${p.kind === "math" ? "math/" + p.data.kind + "/" + p.id : p.kind === "code" ? "code/" + p.data.question_id : "diagrams/" + (p.data.question_id === "TN1-Q010" ? "salt" : p.data.question_id === "TN1-Q011" ? "lamport" : p.data.question_id === "TN1-Q074" ? "network" : "hash")}">Làm lại bài này</a></div>`,
            )
            .join("")
        : '<p class="muted">Chưa có phép tính hoặc bài điền sai. Mỗi lần luyện có đáp án sẽ được giữ trong lịch sử.</p>'
    }</section>`;
}
function bankView() {
  main.innerHTML =
    heading(
      "80 MỤC CHÍNH · GIỮ NGUYÊN ĐỀ",
      "Đề cương & chứng cứ",
      "Đáp án tuần đầu được đối chiếu theo trang slide. Câu chưa có đáp án vẫn đọc được nguyên văn; không có điểm thành thạo giả.",
    ) +
    `<input id="search" class="search" type="text" placeholder="Tìm theo chủ đề, câu hỏi hoặc mã Q…" aria-label="Tìm câu hỏi"><div class="panel"><div id="bank-rows">${cardRows(bank.questions.map((q) => q.question_id))}</div></div>`;
  on("#search", "input", (e) => {
    const val = e.target.value.toLocaleLowerCase("vi");
    document.querySelector("#bank-rows").innerHTML = cardRows(
      bank.questions
        .filter((q) =>
          (q.original_text + " " + q.section_id + " " + q.question_id)
            .toLocaleLowerCase("vi")
            .includes(val),
        )
        .map((q) => q.question_id),
    );
  });
}
let mathKind = "rsa",
  mathResult = null,
  stepIndex = 0;
function mathView(kind = mathKind, practiceId) {
  if (!(kind in boot.math)) kind = "rsa";
  mathKind = kind;
  mathResult = null;
  stepIndex = 0;
  const p = boot.math[kind];
  main.innerHTML =
    heading(
      "SỐ HỌC CHÍNH XÁC",
      "Bảng thực hành mật mã",
      "Luyện trên số nhỏ của đề cương. Chọn xem mẫu, giảm dần gợi ý hoặc tự giải rồi kiểm tra kết quả.",
    ) +
    `<div class="tabs">${Object.keys(boot.math)
      .map(
        (k) =>
          `<button data-math="${k}" class="${k === kind ? "active" : ""}">${k.toUpperCase()}</button>`,
      )
      .join(
        "",
      )}</div><div class="math-layout"><section class="panel"><h2>${esc(p.title)}</h2><div class="source-links">${src("outline", q(p.question_id).pdf_page)}<a href="${esc(p.url)}" target="_blank" rel="noopener">Chuẩn thuật toán ↗</a></div><p class="hint-text">${esc(p.source)}</p><div id="formula" class="formula"></div><div class="form-grid">${p.fields.map((f) => `<label for="m-${f}">${f}<input id="m-${f}" type="text" inputmode="numeric" value="${p.values[f]}"></label>`).join("")}</div><div class="note">Nếu thay dữ kiện, đây là bài luyện tự chọn, không còn là nguyên văn đề. Bài ElGamal 1 thiếu k; ECC 2 ghi mod 1. Không tự sửa. ECC mã hóa thông điệp số cần quy tắc ánh xạ số sang điểm được nêu rõ.</div><label class="field" for="math-mode">Mức hỗ trợ</label><select id="math-mode"><option value="worked">Xem mẫu · tất cả các bước</option><option value="faded">Giảm gợi ý · mở lần lượt từng bước</option><option value="solo">Tự giải · phải nhập kết quả trước</option></select><label class="field" for="math-answer">${esc(p.target)}</label><input id="math-answer" type="text" placeholder="Nhập kết quả để được kiểm tra và lưu"><div class="actions" style="margin-top:20px"><button class="primary" id="math-check">Tính & kiểm tra</button><button id="math-clear">Đặt lại dữ kiện</button></div><div id="math-feedback"></div></section><section class="panel"><div class="row"><h2>Quan sát từng bước</h2><span class="pill">EXACT INTEGER</span></div><div id="math-steps" class="empty">Bắt đầu từ dữ kiện bên trái.<br>Kết quả và các bước sẽ xuất hiện ở đây.</div><div id="math-graph"></div></section></div>`;
  katex.render(p.formula, document.querySelector("#formula"), {
    throwOnError: false,
    displayMode: true,
  });
  if (practiceId) {
    const saved = state.practices.find((x) => x.id === practiceId);
    if (saved) {
      const v = JSON.parse(saved.payload).values;
      for (const key of p.fields)
        document.querySelector("#m-" + key).value = v[key];
      document.querySelector("#math-mode").value = "solo";
    }
  }
  on("[data-math]", "click", (e) => mathView(e.currentTarget.dataset.math));
  on("#math-clear", "click", () => mathView(kind));
  on(
    "#math-check",
    "click",
    guarded(async () => {
      const values = Object.fromEntries(
        p.fields.map((f) => [f, document.querySelector("#m-" + f).value]),
      );
      const mode = document.querySelector("#math-mode").value;
      mathResult = await api("math", {
        kind,
        values,
        mode,
        answer: document.querySelector("#math-answer").value,
      });
      stepIndex = mode === "faded" ? 1 : mathResult.steps.length;
      document.querySelector("#math-feedback").innerHTML =
        `<div class="${mathResult.correct === false ? "error-box" : "success"}" style="margin-top:17px"><b>${mathResult.correct === null && mode === "faded" ? "Mở dần từng bước, tự dự đoán kết quả trước." : (mathResult.correct === null ? "Kết quả mẫu" : mathResult.correct ? "Đúng · đã lưu bài luyện" : "Chưa đúng · đã ghi vào lịch sử") + ": " + esc(mathResult.expected)}</b>${mathResult.correct === null ? "<br>Xem mẫu chưa được tính là tự giải." : ""}</div>`;
      renderMathSteps(mode);
      if (mathResult.points.length) plotECC(mathResult);
      await refresh();
    }),
  );
}
function renderMathSteps(mode) {
  const visible = mathResult.steps.slice(0, stepIndex);
  document.querySelector("#math-steps").className = "";
  document.querySelector("#math-steps").innerHTML =
    visible
      .map(
        (s, i) =>
          `<div class="step ${i === stepIndex - 1 ? "active" : ""}"><span class="number">${i + 1}</span><span>${esc(s)}</span></div>`,
      )
      .join("") +
    (mode === "faded" && stepIndex < mathResult.steps.length
      ? '<button id="next-step" style="margin-top:15px">Mở bước tiếp theo →</button>'
      : "");
  on("#next-step", "click", () => {
    stepIndex++;
    renderMathSteps(mode);
  });
}
function plotECC(r) {
  const p = r.values.p,
    size = 320,
    pad = 35,
    scale = (size - 2 * pad) / (p - 1);
  const coords = (x, y) => [pad + x * scale, size - pad - y * scale];
  let svg = `<svg class="finite-plot" viewBox="0 0 ${size} ${size + 35}" role="img" aria-label="Các điểm của đường cong trên trường hữu hạn"><rect width="${size}" height="${size}" fill="#fafcfb"/>`;
  for (let i = 0; i < p; i++) {
    const v = pad + i * scale;
    svg += `<line x1="${v}" y1="${pad}" x2="${v}" y2="${size - pad}" stroke="#e1e9e5"/><line x1="${pad}" y1="${v}" x2="${size - pad}" y2="${v}" stroke="#e1e9e5"/>`;
    if (p <= 19)
      svg += `<text x="${v}" y="${size - pad + 17}" text-anchor="middle" font-size="9" fill="#708276">${i}</text><text x="${pad - 13}" y="${size - pad - i * scale + 3}" text-anchor="middle" font-size="9" fill="#708276">${i}</text>`;
  }
  for (const [x, y] of r.points) {
    const [cx, cy] = coords(x, y),
      sel = r.selected && x === r.selected[0] && y === r.selected[1];
    svg += `<circle data-point="${x},${y}" cx="${cx}" cy="${cy}" r="${p > 31 ? 2.5 : 5}" fill="${sel ? "#ce8444" : "#208576"}" tabindex="0" role="button" aria-label="Điểm (${x},${y})"><title>(${x}, ${y})${sel ? " · kết quả" : ""}</title></circle>`;
  }
  svg += `<text x="${size / 2}" y="${size + 18}" text-anchor="middle" font-size="12" fill="#56736a">Điểm rời rạc trên F${p} · không nối thành đường liên tục</text></svg>`;
  document.querySelector("#math-graph").innerHTML =
    `<h3 style="margin-top:22px">Đường cong trên trường hữu hạn</h3>${svg}<p id="point-info" class="hint-text">Chọn một điểm để đọc tọa độ. O là điểm vô cực, không nằm trên mặt phẳng này.</p>`;
  const select = (e) => {
    document.querySelector("#point-info").textContent =
      `Điểm (${e.currentTarget.dataset.point}) thỏa y² ≡ x³+ax+b (mod ${p}).`;
  };
  on("[data-point]", "click", select);
  on("[data-point]", "keydown", (e) => {
    if (["Enter", " "].includes(e.key)) select(e);
  });
}
const diagrams = {
  hash: {
    title: "Xác thực lưu băm",
    id: "TN1-Q009",
    page: 139,
    messages: [
      "Alice, Pass",
      "Tra cứu h(P_A)",
      "h(Pass) = h(P_A)?",
      "Grant / Deny",
    ],
    question: "Bob phải so sánh h(Pass) với giá trị nào đã lưu?",
    expected: "h(P_A)",
    explain:
      "Bob lưu h(P_A), không cần lưu P_A rõ. Pass vẫn được truyền trong giao thức; băm trong CSDL không tự bảo vệ đường truyền.",
  },
  salt: {
    title: "Xác thực có salt",
    id: "TN1-Q010",
    page: 140,
    messages: [
      "Alice, Pass",
      "Tra cứu S_A, h(P_A ∥ S_A)",
      "h(Pass ∥ S_A) = h(P_A ∥ S_A)?",
      "Grant / Deny",
    ],
    question: "Đầu vào hàm băm khi Bob kiểm tra là gì?",
    expected: "Pass||S_A",
    explain:
      "Theo slide 140, ghép mật khẩu trước, salt sau. Salt làm bảng băm sẵn dùng chung khó áp dụng; vẫn có thể dò từng tài khoản.",
  },
  lamport: {
    title: "Lamport · mật khẩu một lần",
    id: "TN1-Q011",
    page: 142,
    messages: [
      "Alice",
      "Bob gửi chỉ số n",
      "Alice gửi h^(n−1)(P0)",
      "Băm một lần, so sánh h^n(P0)",
    ],
    question: "Bob băm bao nhiêu lần trên giá trị Alice vừa gửi để kiểm tra?",
    expected: "1",
    explain:
      "Nếu khớp, lưu giá trị vừa nhận và giảm n. Giới hạn MITM trong slide: giả chỉ số thấp hơn để lấy giá trị có thể băm tiếp.",
  },
  network: {
    title: "Phòng thủ nhiều lớp",
    id: "TN1-Q074",
    page: 69,
    messages: [
      "Biên mạng · firewall",
      "Dịch vụ công khai · vùng DMZ",
      "Mạng nội bộ · phân đoạn",
      "Thu thập log · SIEM",
    ],
    question: "Thành phần nào thu thập, lưu trữ, phân tích log tập trung?",
    expected: "SIEM",
    explain:
      "Sơ đồ vận dụng DERIVED từ slide 69, 330–331, 365,375,378; DMZ/phân đoạn là cách đề xuất bố trí, không phải nguyên văn mô hình của slide69.",
  },
};
let diagramKind = "hash",
  diagramStep = 0,
  diagramHidden = false;
function diagramsView(kind = diagramKind) {
  diagramKind = kind;
  diagramStep = 0;
  diagramHidden = false;
  const d = diagrams[kind];
  main.innerHTML =
    heading(
      "TÁI HIỆN BẰNG SƠ ĐỒ",
      "Giao thức & kiến trúc mạng",
      "Quan sát từng bước, ẩn thông điệp và tự điền. Sơ đồ SVG có thể đọc rõ khi phóng to.",
    ) +
    `<div class="tabs">${Object.entries(diagrams)
      .map(
        ([k, d]) =>
          `<button data-diagram="${k}" class="${kind === k ? "active" : ""}">${d.title}</button>`,
      )
      .join(
        "",
      )}</div><div class="grid"><section class="panel"><h2>${d.title}</h2><div class="source-links">${src("slide", d.page)}${src("outline", kind === "lamport" ? 3 : kind === "network" ? q(d.id).pdf_page : 2)}</div><div id="diagram-svg"></div><div class="actions" style="margin-top:20px"><button id="diagram-next">Tô sáng bước tiếp →</button><button id="diagram-hide">Ẩn thông điệp</button></div><p id="diagram-caption" class="hint-text" style="margin-top:15px"></p></section><section class="panel"><div class="eyebrow">TỰ ĐIỀN TRƯỚC KHI ĐỐI CHIẾU</div><h2>${d.question}</h2><label class="field" for="diagram-answer">Câu trả lời</label><input id="diagram-answer" type="text" placeholder="Với phép ghép, dùng ||"><button id="diagram-check" class="primary" style="margin-top:17px">Kiểm tra & xem cơ chế</button><div id="diagram-feedback"></div><p class="hint-text" style="margin-top:17px">Bài điền kiểm tra một thành phần, không thay thế bài tự luận đủ bốn ý.</p><a class="button small" href="#card/${d.id}/${day}">Viết lại toàn bộ giao thức →</a></section></div>`;
  renderDiagram();
  on("[data-diagram]", "click", (e) =>
    diagramsView(e.currentTarget.dataset.diagram),
  );
  on("#diagram-next", "click", () => {
    diagramStep = (diagramStep + 1) % 4;
    renderDiagram();
  });
  on("#diagram-hide", "click", () => {
    diagramHidden = !diagramHidden;
    renderDiagram();
    document.querySelector("#diagram-hide").textContent = diagramHidden
      ? "Hiện thông điệp"
      : "Ẩn thông điệp";
  });
  on(
    "#diagram-check",
    "click",
    guarded(async () => {
      const answer = document.querySelector("#diagram-answer").value.trim();
      if (!answer) throw Error("Hãy tự điền một đáp án trước.");
      const normalize = (s) =>
        s
          .toLowerCase()
          .replace(/[\s_()]/g, "")
          .replaceAll("∥", "||");
      const correct = normalize(answer) === normalize(d.expected);
      await api("practice", {
        kind: "diagram",
        payload: {
          question_id: d.id,
          answer,
          correct,
          expected: d.expected,
          assessment: "exact_fill",
        },
      });
      document.querySelector("#diagram-feedback").innerHTML =
        `<div class="${correct ? "success" : "error-box"}" style="margin-top:20px"><b>${correct ? "Đúng" : "Chưa khớp"} · ${esc(d.expected)}</b><p style="margin-top:12px">${esc(d.explain)}</p></div>`;
      await refresh();
    }),
  );
}
function renderDiagram() {
  const d = diagrams[diagramKind];
  let svg = `<svg class="diagram" viewBox="0 0 650 390" role="img" aria-label="${esc(d.title)}"><defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#577c8d"/></marker></defs>`;
  if (diagramKind === "network") {
    const positions = [
      [45, 55],
      [360, 55],
      [45, 230],
      [360, 230],
    ];
    d.messages.forEach((m, i) => {
      const [x, y] = positions[i];
      svg += `<rect class="box ${i === diagramStep ? "highlight" : ""}" x="${x}" y="${y}" width="235" height="85" rx="10"/><text x="${x + 117}" y="${y + 48}" text-anchor="middle">${diagramHidden ? "Thành phần " + (i + 1) : esc(m)}</text>`;
    });
    svg +=
      '<path class="line" marker-end="url(#arrow)" d="M280 97 H353"/><path class="line" marker-end="url(#arrow)" d="M162 140 V223"/><path class="line" marker-end="url(#arrow)" d="M280 273 H353"/><path class="line" marker-end="url(#arrow)" d="M478 140 V223"/><text x="320" y="355" text-anchor="middle">DERIVED · Sơ đồ luyện bố trí các lớp bảo vệ</text>';
  } else {
    svg +=
      '<rect class="box" x="48" y="22" width="150" height="44" rx="9"/><rect class="box" x="447" y="22" width="150" height="44" rx="9"/><text class="label" x="123" y="50" text-anchor="middle">Alice · Khai báo</text><text class="label" x="522" y="50" text-anchor="middle">Bob · Kiểm tra</text><path class="line" stroke-dasharray="5 6" d="M123 66 V370 M522 66 V370"/>';
    d.messages.forEach((m, i) => {
      const y = 110 + i * 75,
        back = diagramKind === "lamport" && i === 1,
        internal = diagramKind === "lamport" ? i === 3 : i > 0;
      if (internal)
        svg += `<rect x="${i === 1 ? 408 : 315}" y="${y - 23}" width="${i === 1 ? 210 : 310}" height="43" rx="6" fill="${i === diagramStep ? "#d2e8dd" : "#eef2f4"}"/>`;
      else
        svg += `<line class="line ${i === diagramStep ? "highlight" : ""}" x1="${back ? 514 : 132}" y1="${y}" x2="${back ? 133 : 513}" y2="${y}" marker-end="url(#arrow)"/>`;
      svg += `<text x="${internal ? (i === 1 ? 513 : 470) : 325}" y="${internal ? y + 4 : y - 12}" text-anchor="middle" class="${diagramHidden ? "hidden-label" : ""}">${diagramHidden ? "Thông điệp / bước " + (i + 1) : esc(m)}</text>`;
    });
  }
  svg += "</svg>";
  document.querySelector("#diagram-svg").innerHTML = svg;
  document.querySelector("#diagram-caption").textContent =
    `Bước ${diagramStep + 1}/4${diagramHidden ? " · Nhớ lại nội dung trước khi hiện." : ": " + d.messages[diagramStep]}`;
}
const codeCases = {
  "TN1-Q028": {
    line: "strcpy(buffer, input);",
    page: 311,
    title: "C · sao chép vào bộ đệm",
    answer:
      "buffer chỉ có 10 byte kể cả ký tự kết thúc. strcpy không kiểm tra dung lượng đích; chuỗi lớn làm ghi ngoài biên bộ đệm trên stack, dẫn đến hành vi không xác định, có thể crash hoặc làm hỏng dữ liệu điều khiển. Không thể khẳng định chiếm quyền thành công trên mọi môi trường. Kiểm tra độ dài trước khi sao chép và giới hạn dung lượng; nếu dùng snprintf phải kiểm tra kết quả cắt ngắn. Bảo vệ DEP/ASLR/canary là lớp bổ sung, không sửa phép ghi ngoài biên.",
    source:
      "DERIVED · phân tích mã nguyên văn; SLIDE_GROUNDED · định nghĩa PDF303, phân loại307, minh họa strcpy311, bảo vệ312–313.",
  },
  "TN1-Q029": {
    line: "gets(buffer);",
    page: 303,
    title: "C · đọc đầu vào không giới hạn",
    answer:
      "gets đọc đến newline mà không biết kích thước buffer[8]. Đầu vào dài hơn 7 ký tự có thể tràn khi thêm ký tự kết thúc. Dùng fgets(buffer,sizeof buffer,stdin), kiểm tra giá trị trả về và xử lý dòng còn dư khi cần. Tràn stack gây hành vi không xác định; khả năng khai thác phụ thuộc môi trường.",
    source:
      "DERIVED · phân tích đoạn mã; SLIDE_GROUNDED · PDF303,307; EXTERNAL · gets đã bị loại khỏi C11 (WG14 N1570).",
  },
};
let codeKind = "TN1-Q028",
  selectedLines = new Set();
function codeView(id = codeKind) {
  codeKind = id;
  selectedLines = new Set();
  const c = codeCases[id],
    original = q(id).original_text;
  const code = original
    .slice(original.indexOf("#include"), original.indexOf("Hãy xác định"))
    .trim();
  const lines = code.split("\n");
  main.innerHTML =
    heading(
      "PHÁT HIỆN TRƯỚC · GIẢI THÍCH SAU",
      "Đọc mã nguồn tìm lỗi",
      "Mã giữ nguyên theo đề cương. Chọn dòng nghi vấn, viết cơ chế và cách sửa rồi mới mở phần đối chiếu.",
    ) +
    `<div class="tabs">${Object.entries(codeCases)
      .map(
        ([k, c]) =>
          `<button data-code="${k}" class="${id === k ? "active" : ""}">${short(k)} · ${c.title}</button>`,
      )
      .join(
        "",
      )}</div><div class="grid"><section class="panel"><div class="row"><h2>${c.title}</h2>${src("outline", q(id).pdf_page)}</div><div class="code-view">${lines.map((line, i) => `<div class="code-line" data-line="${i + 1}" tabindex="0" role="button" aria-pressed="false"><span class="line-no">${i + 1}</span><code>${esc(line)}</code></div>`).join("")}</div><p class="hint-text" style="margin-top:12px">Bấm hoặc Enter để đánh dấu dòng. Các dòng gốc không bị sửa khi trình bày.</p></section><section class="panel"><h2>Bạn phát hiện điều gì?</h2><label class="field" for="code-answer">Lỗi · cơ chế · cách loại bỏ</label><textarea id="code-answer" placeholder="Vùng nhớ nào? Thao tác nào? Khi nào vượt giới hạn? Sửa tận gốc ra sao?">${esc(state.drafts["code-" + id] || "")}</textarea><p id="save-status" class="hint-text">Tự lưu bản nháp.</p><button id="code-check" class="primary">Nộp phân tích & đối chiếu</button><div id="code-feedback"></div></section></div>`;
  on("[data-code]", "click", (e) => codeView(e.currentTarget.dataset.code));
  const toggle = (e) => {
    const el = e.currentTarget,
      n = Number(el.dataset.line);
    selectedLines.has(n) ? selectedLines.delete(n) : selectedLines.add(n);
    el.classList.toggle("selected", selectedLines.has(n));
    el.setAttribute("aria-pressed", selectedLines.has(n));
  };
  on("[data-line]", "click", toggle);
  on("[data-line]", "keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      toggle(e);
    }
  });
  on("#code-answer", "input", () => {
    const answer = document.querySelector("#code-answer").value;
    scheduleSave("code-" + id, async () => {
      await api("draft", { key: "code-" + id, answer });
      state.drafts["code-" + id] = answer;
      if (document.querySelector("#save-status"))
        document.querySelector("#save-status").textContent = "Đã lưu bản nháp.";
    });
  });
  on(
    "#code-check",
    "click",
    guarded(async () => {
      const answer = document.querySelector("#code-answer").value.trim();
      if (!selectedLines.size || answer.length < 3)
        throw Error("Chọn ít nhất một dòng nghi vấn và viết phân tích trước.");
      const target = lines.findIndex((l) => l.includes(c.line)) + 1,
        located = selectedLines.has(target);
      await api("practice", {
        kind: "code",
        payload: {
          question_id: id,
          answer,
          lines: [...selectedLines],
          located,
          assessment: "line_detection_only",
        },
      });
      document
        .querySelector(`[data-line="${target}"]`)
        .classList.add("checked");
      document.querySelector("#code-feedback").innerHTML =
        `<div class="${located ? "success" : "error-box"}" style="margin-top:18px"><b>${located ? "Đã chọn dòng nguy hiểm" : "Cần kiểm tra dòng " + target}</b><p style="margin-top:12px">${esc(c.answer)}</p><p class="hint-text">${esc(c.source)}</p>${[303, 307, 311, 312, 313].map((p) => src("slide", p)).join(" · ")}<div class="note">Kết quả trên chỉ kiểm tra vị trí dòng. Hãy tự đối chiếu cơ chế và cách sửa; chưa có chấm ngữ nghĩa tự động.</div></div>`;
      await refresh();
    }),
  );
}
function examsView() {
  exam = null;
  main.innerHTML =
    heading(
      "TỰ LUẬN · CÓ ĐỒNG HỒ",
      "Phòng thi thử",
      "Viết lời giải khi đáp án đang ẩn. Bài và thời điểm kết thúc được lưu trên máy, có thể mở lại phiên đang làm.",
    ) +
    `<div class="section-grid">${[
      [
        "baseline",
        "Kiểm tra đầu vào",
        45,
        "5 câu nền tảng tự chọn · đáp án/rubric sẵn sàng",
      ],
      [
        "week1",
        "Kiểm tra cuối tuần 1",
        45,
        "5 câu truy xuất trộn · đáp án/rubric sẵn sàng",
      ],
      [
        "sample1",
        "Đề mẫu số 1",
        180,
        "5 câu nguyên văn · đáp án chưa kiểm chứng đầy đủ",
      ],
      [
        "sample2",
        "Đề mẫu số 2",
        180,
        "5 câu nguyên văn · đáp án chưa kiểm chứng đầy đủ",
      ],
      [
        "sample3",
        "Đề mẫu số 3",
        180,
        "5 câu nguyên văn · đáp án chưa kiểm chứng đầy đủ",
      ],
    ]
      .map(
        ([kind, title, mins, note]) =>
          `<section class="panel"><span class="pill ${kind.startsWith("sample") ? "amber" : "green"}">${mins} phút</span><h2 style="margin-top:15px">${title}</h2><p class="muted">${note}</p><button class="primary" data-exam="${kind}">Vào phòng thi →</button></section>`,
      )
      .join(
        "",
      )}</div><section class="panel" style="margin-top:24px"><h2>Các phiên thi đã lưu</h2>${
      state.exams.length
        ? state.exams
            .slice()
            .reverse()
            .map(
              (e) =>
                `<div class="qrow"><div class="qtext"><strong>${esc(e.kind)}</strong><small>${new Date(e.started).toLocaleString("vi-VN")}</small></div><span class="pill">${e.finished ? "Đã nộp" : "Đang làm"}</span><a class="button small" href="#exam/${e.id}">${e.finished ? "Xem báo cáo" : "Tiếp tục"}</a></div>`,
            )
            .join("")
        : '<p class="muted">Chưa có phiên thi. Bắt đầu với kiểm tra đầu vào.</p>'
    }</section>`;
  on(
    "[data-exam]",
    "click",
    guarded(async (e) => {
      const result = await api("exam/start", {
        kind: e.currentTarget.dataset.exam,
      });
      await refresh();
      location.hash = "exam/" + result.id;
    }),
  );
}
function examView(id) {
  exam = state.exams.find((e) => e.id === id);
  if (!exam) return examsView();
  if (exam.finished) return examReport();
  const ids = boot.exam_sets[exam.kind];
  main.innerHTML = `<div class="narrow"><div class="exam-head row"><div><div class="eyebrow">${exam.kind.startsWith("sample") ? "ĐỀ MẪU NGUYÊN VĂN" : "ĐỀ LUYỆN TỰ CHỌN"}</div><h2 style="margin-bottom:0">Phiên thi tự luận</h2><span class="hint-text" id="exam-save">Bài được tự lưu.</span></div><div class="timer" id="timer"></div><button id="exam-finish" class="primary">Nộp bài & đối chiếu</button></div><div class="note">${exam.kind.startsWith("sample") ? "Đề mẫu gốc được giữ nguyên. Những câu chưa có đáp án kiểm chứng chỉ lưu bài và ghi trạng thái chờ; chưa chấm điểm cho chúng." : "Rubric được mở sau khi nộp. Tự đối chiếu từng ý, không chấm ngữ nghĩa bằng từ khóa."}</div>${ids.map((id, i) => `<section class="panel"><div class="row"><h2>Câu ${i + 1}</h2>${src("outline", q(id).pdf_page)}</div><div class="long-question">${esc(q(id).original_text)}</div>${/sơ đồ|mô hình/i.test(q(id).original_text) ? `<details><summary>Mở trang đề gốc có hình</summary><a href="/sources/outline.pdf#page=${q(id).pdf_page}" target="_blank" rel="noopener"><img src="/figures/outline-${q(id).pdf_page}.png" style="width:100%;height:auto" alt="Trang ${q(id).pdf_page} đề cương nguyên gốc"></a></details>` : ""}<label class="field" for="exam-${id}">Bài làm của bạn</label><textarea id="exam-${id}" data-exam-answer="${id}" rows="8">${esc(exam.answers[id] || "")}</textarea></section>`).join("")}</div>`;
  on(
    "[data-exam-answer]",
    "input",
    guarded(async (e) => {
      const current = exam;
      current.answers[e.target.dataset.examAnswer] = e.target.value;
      document.querySelector("#exam-save").textContent = "Đang lưu…";
      scheduleSave("exam-" + current.id, async () => {
        const saved = await api("exam/save", {
          id: current.id,
          answers: current.answers,
        });
        exam = saved;
        if (document.querySelector("#exam-save"))
          document.querySelector("#exam-save").textContent = "Đã lưu trên máy.";
        if (saved.finished) setTimeout(() => route(), 0);
      });
    }),
  );
  const finish = guarded(async () => {
    const button = document.querySelector("#exam-finish");
    if (button) button.disabled = true;
    await flushSaves();
    exam = await api("exam/finish", { id: exam.id, answers: exam.answers });
    await refresh();
    clearInterval(examTimer);
    examReport();
  });
  on("#exam-finish", "click", finish);
  const tick = () => {
    const seconds = Math.max(
      0,
      Math.ceil((new Date(exam.deadline) - Date.now()) / 1000),
    );
    const timer = document.querySelector("#timer");
    if (!timer) return;
    timer.textContent = `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
    if (seconds <= 0) {
      clearInterval(examTimer);
      finish();
    }
  };
  tick();
  examTimer = setInterval(tick, 1000);
}
function examReport() {
  const current = exam;
  main.innerHTML = `<div class="narrow">${heading("BÀI THI ĐÃ LƯU", "Báo cáo đối chiếu", "Ứng dụng giữ nguyên bài bạn viết. Thang dưới đây đánh giá độ phủ ý theo tự đối chiếu; điểm tự luận chính thức cần người chấm.")}<p class="hint-text">Phiên ${esc(current.kind)} · ${new Date(current.started).toLocaleString("vi-VN")}</p>${Object.entries(
    current.report || {},
  )
    .map(([id, r], i) => {
      const already = state.attempts.find((a) => a.id === r.attempt_id);
      return `<section class="panel"><h2>Câu ${i + 1} · ${short(id)}</h2><div class="long-question">${esc(q(id).original_text)}</div><details open><summary>Bài đã nộp</summary><p style="white-space:pre-wrap;margin-top:12px">${esc(r.answer || "(Chưa trả lời)")}</p></details>${r.card ? `<h3 style="margin-top:20px">Đáp án & thang tự đối chiếu</h3><p class="answer">${esc(r.card.answer)}</p>${sourcePanel(r.card)}<div class="rubric" data-exam-rubric="${id}">${rubricHtml(r.card, "exam-" + id)}</div>${already?.graded ? `<div class="info">Đã lưu: ${already.score}%. ${esc(already.error || "Đủ ý theo tự đối chiếu.")}</div>` : r.attempt_id ? `<button class="primary" data-exam-grade="${id}" style="margin-top:15px">Lưu rubric & báo ý thiếu</button>` : '<div class="note">Không có bài trả lời, chưa tính một lần ôn. Hãy học lại câu này.</div>'}<div id="result-${id}"></div>` : '<div class="note">AWAITING_REVIEW · Chưa có đáp án/rubric kiểm chứng. Bài đã được lưu, không tạo điểm giả.</div>'}</section>`;
    })
    .join("")}<a class="button" href="#exams">Về phòng thi</a></div>`;
  on(
    "[data-exam-grade]",
    "click",
    guarded(async (e) => {
      const id = e.currentTarget.dataset.examGrade,
        r = current.report[id];
      const checked = [
        ...document.querySelectorAll(`input[name="exam-${id}"]:checked`),
      ].map((x) => x.value);
      const result = await api("grade", {
        attempt_id: r.attempt_id,
        checks: checked,
        confidence: 2,
        error: "",
      });
      e.currentTarget.disabled = true;
      document.querySelector("#result-" + id).innerHTML =
        `<div class="info">${result.score}% · Ôn ${dateText(result.due)}. ${result.missing.length ? "Ý thiếu: " + result.missing.map(esc).join("; ") : "Đủ ý theo tự đối chiếu."}</div>`;
      await refresh();
    }),
  );
}
function settingsView() {
  const schedule = state.settings.schedule || {};
  main.innerHTML =
    heading(
      "TIẾN ĐỘ BỀN VỮNG",
      "Lịch học & sao lưu",
      "Bài làm lưu trong SQLite trên máy. Đổi lịch không xóa bài cũ; lịch ôn từng câu vẫn theo ngày thực tế.",
    ) +
    `<div class="grid"><section class="panel"><h2>Dời các phiên học</h2><p class="hint-text">Ngày gốc 12/10–01/12. Đặt lại một ngày hoặc dùng chức năng dời phần còn lại.</p><div class="form-grid"><label>Từ ngày số<input id="shift-day" type="number" min="1" max="51" value="${day}"></label><label>Ngày mới<input id="shift-date" type="date" value="${schedule[day] || bank.plan[day - 1].date}"></label></div><button class="primary" id="shift-all" style="margin:17px 0">Dời từ ngày này trở đi</button><details><summary>Điều chỉnh từng ngày</summary>${bank.plan.map((p) => `<label class="schedule-row"><span>${p.day}. ${esc(p.title)}</span><input type="date" data-schedule="${p.day}" value="${schedule[p.day] || p.date}"></label>`).join("")}<button id="save-schedule" style="margin-top:15px">Lưu lịch từng ngày</button></details></section><section class="panel"><h2>Sao lưu bài làm</h2><p>Xuất bản sao JSON để chuyển máy hoặc giữ một bản riêng. Khôi phục sẽ hợp nhất lịch sử, giữ bài đã có.</p><button class="primary" id="export">Tải bản sao tiến độ</button><label class="field" for="restore">Khôi phục từ bản sao JSON</label><input class="file-input" id="restore" type="file" accept="application/json,.json"><div class="info">Không có tài khoản hay đồng bộ đám mây. Đừng đưa bản sao bài làm vào kho tài liệu công khai nếu không cần.</div><h3>Phạm vi bản hiện tại</h3><p class="hint-text">80 câu gốc, 51 phiên học; 23 đáp án lý thuyết tuần đầu, 5 bảng thuật toán, 4 sơ đồ, 2 bài đọc mã, 2 bài thi có rubric sẵn sàng. Ba đề mẫu gốc có đồng hồ/lưu bài, chưa đủ đáp án kiểm chứng.</p></section></div>`;
  on(
    "#export",
    "click",
    guarded(async () => {
      const data = await api("export"),
        url = URL.createObjectURL(
          new Blob([JSON.stringify(data, null, 2)], {
            type: "application/json",
          }),
        );
      const a = document.createElement("a");
      a.href = url;
      a.download = "TN1-tien-do-" + boot.today + ".json";
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    }),
  );
  on(
    "#restore",
    "change",
    guarded(async (e) => {
      const f = e.target.files[0];
      if (!f) return;
      if (f.size > 8_000_000) throw Error("Bản sao quá 8 MB.");
      await api("restore", JSON.parse(await f.text()));
      await refresh();
      toast("Đã hợp nhất bản sao tiến độ.");
      settingsView();
    }),
  );
  on(
    "#save-schedule",
    "click",
    guarded(async () => {
      const value = {};
      document.querySelectorAll("[data-schedule]").forEach((e) => {
        if (e.value) value[e.dataset.schedule] = e.value;
      });
      await api("settings", { key: "schedule", value });
      await refresh();
      toast("Đã lưu lịch học.");
    }),
  );
  on(
    "#shift-all",
    "click",
    guarded(async () => {
      const n = Number(document.querySelector("#shift-day").value),
        value = { ...schedule },
        start = document.querySelector("#shift-date").value;
      if (!start || n < 1 || n > 51) throw Error("Chọn ngày bắt đầu hợp lệ.");
      const d = new Date(start + "T12:00:00");
      for (let i = n; i <= 51; i++) {
        value[i] =
          `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
        d.setDate(d.getDate() + 1);
      }
      await api("settings", { key: "schedule", value });
      await refresh();
      toast("Đã dời lịch; lịch sử được giữ nguyên.");
      settingsView();
    }),
  );
}
async function route() {
  clearInterval(examTimer);
  const [name, arg, n] = (location.hash.slice(1) || "day/" + day).split("/");
  document
    .querySelectorAll("[data-nav]")
    .forEach((el) =>
      el.classList.toggle(
        "active",
        el.dataset.nav === name ||
          (name === "card" && el.dataset.nav === "day") ||
          (name === "exam" && el.dataset.nav === "exams"),
      ),
    );
  document.querySelector("#breadcrumb").textContent =
    {
      day: "Phiên học mỗi ngày",
      card: "Truy xuất & đối chiếu",
      plan: "Lộ trình học",
      review: "Ôn tập & câu sai",
      bank: "Đề cương & nguồn",
      math: "Thực hành mật mã",
      diagrams: "Sơ đồ tương tác",
      code: "Đọc mã tìm lỗi",
      exams: "Phòng thi",
      exam: "Bài thi tự luận",
      settings: "Lịch & sao lưu",
    }[name] || "Không gian học tập";
  try {
    await flushSaves();
    await refresh();
    (
      ({
        day: () => dayView(arg),
        card: () => cardView(arg, n),
        plan: planView,
        review: reviewView,
        bank: bankView,
        math: () => mathView(arg || mathKind, n),
        diagrams: () => diagramsView(arg || diagramKind),
        code: () => codeView(arg || codeKind),
        exams: examsView,
        exam: () => examView(arg),
        settings: settingsView,
      })[name] || (() => dayView(1))
    )();
    window.scrollTo(0, 0);
  } catch (e) {
    main.innerHTML = `<div class="error-box">Không mở được phiên học: ${esc(e.message)}. Kiểm tra cửa sổ chạy ứng dụng rồi tải lại.</div>`;
  }
}
window.addEventListener("hashchange", route);
refresh()
  .then(() => {
    const dateIndex = bank.plan.findIndex(
      (p) =>
        (state.settings.schedule || {})[p.day] === boot.today ||
        (!(state.settings.schedule || {})[p.day] && p.date === boot.today),
    );
    day = dateIndex >= 0 ? dateIndex + 1 : 1;
    document.querySelector("[data-nav=day]").href = "#day/" + day;
    route();
  })
  .catch((e) => {
    main.innerHTML = `<p class="error-box">Không kết nối được ứng dụng: ${esc(e.message)}</p>`;
  });
