/* Reusable, isolated QA. No npm/build dependency for the study application. */
const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");
const { spawn } = require("node:child_process");
const assert = require("node:assert/strict");
let playwright;
try {
  playwright = require("playwright");
} catch {
  playwright = require(
    path.join(
      process.env.USERPROFILE || os.homedir(),
      ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright",
    ),
  );
}
const root = path.resolve(__dirname, "..");
const output = path.resolve(
  process.env.QA_OUTPUT || path.join(root, ".qa/browser"),
);
fs.mkdirSync(output, { recursive: true });
const temp = fs.mkdtempSync(path.join(os.tmpdir(), "tn1-browser-"));
const data = path.join(temp, "data"),
  otherData = path.join(temp, "restored");
fs.mkdirSync(data);
fs.mkdirSync(otherData);
const port = Number(process.env.QA_PORT || 8766),
  url = `http://127.0.0.1:${port}`;
const processes = new Set(),
  errors = [],
  external = [],
  passed = [];
let context, serverProcess;
const pause = (ms) => new Promise((r) => setTimeout(r, ms));
async function until(fn, message, ms = 15000) {
  const limit = Date.now() + ms;
  while (Date.now() < limit) {
    if (await fn()) return;
    await pause(20);
  }
  throw Error(message);
}
async function request(route, payload, base = url) {
  const r = await fetch(
    base + "/api/" + route,
    payload === undefined
      ? {}
      : {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        },
  );
  const body = await r.json();
  if (!r.ok) throw Error(body.error);
  return body;
}
async function start(dir, number) {
  const child = spawn(
    process.env.QA_PYTHON || "python",
    [
      "-m",
      "tools.browser_fixture",
      "--port",
      String(number),
      "--data-dir",
      dir,
    ],
    {
      cwd: root,
      windowsHide: true,
      env: { ...process.env, PYTHONIOENCODING: "utf-8" },
    },
  );
  processes.add(child);
  let log = "";
  child.stdout.on("data", (x) => (log += x));
  child.stderr.on("data", (x) => (log += x));
  child.on("error", (e) => (log += e.message));
  await until(
    () =>
      log.includes("QA fixture ready") ||
      (child.exitCode !== null &&
        (() => {
          throw Error(log);
        })()),
    "Server did not start",
  );
  child.qaLog = () => log;
  return child;
}
async function stop(child) {
  if (child.exitCode !== null) return;
  const done = new Promise((r) => child.once("exit", r));
  child.kill();
  await done;
  processes.delete(child);
}
function clock(now) {
  const target = path.join(data, "clock.json");
  const tmp = target + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify({ now }));
  fs.renameSync(tmp, target);
}
async function browser() {
  return playwright.chromium.launchPersistentContext(
    path.join(temp, "browser-profile"),
    {
      headless: true,
      executablePath:
        process.env.QA_CHROME ||
        (process.platform === "win32"
          ? "C:/Program Files/Google/Chrome/Application/chrome.exe"
          : undefined),
      viewport: { width: 1440, height: 1000 },
    },
  );
}
async function newPage() {
  const page = await context.newPage();
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("request", (r) => {
    if (!r.url().startsWith(url)) external.push(r.url());
  });
  return page;
}
let navigation = 0;
async function visit(page, route, selector) {
  await page.goto(url + "/?qa=" + ++navigation + "#" + route);
  await page
    .locator(selector || "main h1")
    .first()
    .waitFor();
  assert(
    !(await page.locator("main").innerText()).includes(
      "Không mở được phiên học",
    ),
  );
}
async function shot(page, name) {
  await page.screenshot({
    path: path.join(output, name + ".png"),
    fullPage: true,
  });
}
async function noOverflow(page, label) {
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > innerWidth + 1,
  );
  if (overflow) {
    await shot(page, "overflow-" + label.replaceAll("/", "-"));
    console.log(
      await page.evaluate(() =>
        [...document.querySelectorAll("main *")]
          .filter((el) => el.getBoundingClientRect().right > innerWidth)
          .map((el) => ({
            tag: el.tagName,
            class: el.className,
            width: el.getBoundingClientRect().width,
          }))
          .slice(0, 15),
      ),
    );
  }
  assert.equal(overflow, false, label + " overflow");
}

(async () => {
  serverProcess = await start(data, port);
  context = await browser();
  let page = await newPage();
  await visit(page, "day/1");
  await shot(page, "home-1440");
  await noOverflow(page, "desktop");
  await visit(page, "card/TN1-Q032/1", "#answer");
  assert.equal(await page.locator("#feedback").innerText(), "");
  await page
    .locator("#answer")
    .fill(
      "ATTT bảo vệ thông tin chống truy cập, sử dụng, tiết lộ, sửa đổi, phá hủy trái phép, bảo đảm CIA.",
    );
  await page.locator("#hint-btn").click();
  await page.locator("#reveal").click();
  await page.locator("#grade").waitFor();
  await shot(page, "recall");
  await page.locator("input[name=r]").first().check();
  await page.locator("#grade").click();
  await page.locator("#grade-result .error-box").waitFor();
  const progress = (await request("bootstrap")).state.progress["TN1-Q032"];
  assert(progress.score < 85 && !progress.mastered);
  passed.push("hidden_answer_hints_rubric_wrong_review");
  await visit(page, "review");
  assert(
    (await page.locator("main").innerText()).includes(
      "TN1-Q032".replace("TN1-", ""),
    ),
  );
  await visit(page, "math", "#math-answer");
  await page.locator("#math-mode").selectOption("solo");
  await page.locator("#math-answer").fill("280");
  await page.locator("#math-check").click();
  await page.locator("#math-feedback").getByText(/Đúng/).waitFor();
  assert((await page.locator(".katex").count()) > 0);
  await page.locator("[data-math=ecc]").click();
  await page.locator("#math-answer").fill("7,9");
  await page.locator("#math-check").click();
  await page.locator(".finite-plot").waitFor();
  await shot(page, "ecc");
  passed.push("exact_RSA_KaTeX_ECC_SVG");
  await visit(page, "diagrams", "#diagram-answer");
  await page.locator("#diagram-hide").click();
  await page.locator("#diagram-next").click();
  await page.locator("#diagram-answer").fill("h(P_A)");
  await page.locator("#diagram-check").click();
  await page.locator("#diagram-feedback").getByText(/Đúng/).waitFor();
  await shot(page, "diagram");
  passed.push("diagram_hide_highlight_fill");
  await visit(page, "code", "#code-answer");
  await page.locator('[data-line="6"]').click();
  await page
    .locator("#code-answer")
    .fill(
      "strcpy không giới hạn kích thước buffer 10 byte, có thể ghi vượt biên; kiểm tra độ dài trước khi sao chép.",
    );
  await page.locator("#code-check").click();
  await page
    .locator("#code-feedback")
    .getByText(/Đã chọn dòng nguy hiểm/)
    .waitFor();
  await shot(page, "code");
  passed.push("source_reader_answer_before_feedback");
  // Close before debounce fires, then close the entire browser and reopen its QA profile.
  await visit(page, "card/TN1-Q013/8", "#answer");
  await page
    .locator("#answer")
    .fill("Nháp giữ qua đóng tab: chỉ cấp quyền tối thiểu đủ làm nhiệm vụ.");
  await page.close();
  await context.close();
  context = await browser();
  page = await newPage();
  await visit(page, "card/TN1-Q013/8", "#answer");
  assert(
    (await page.locator("#answer").inputValue()).includes(
      "Nháp giữ qua đóng tab",
    ),
  );
  await page.goto(url + "/#day/8");
  await page
    .getByRole("heading", { name: "Kiểm soát truy cập", exact: true })
    .waitFor();
  assert((await page.locator("main").innerText()).includes("5/5 đáp án"));
  await shot(page, "day-8");
  passed.push("draft_close_tab_reopen_browser_day_navigation");
  await visit(page, "exams");
  await page.locator("[data-exam=baseline]").click();
  await page.locator("#timer").waitFor();
  await page
    .locator("[data-exam-answer]")
    .nth(0)
    .fill("Câu trả lời A: bảo vệ thông tin.");
  await page.getByText("Đã lưu trên máy chủ.", { exact: true }).waitFor();
  const old = await request("export");
  const oldExam = (await request("bootstrap")).state.exams.at(-1);
  const target = await start(otherData, port + 1);
  await request("restore", old, `http://127.0.0.1:${port + 1}`);
  await page
    .locator("[data-exam-answer]")
    .nth(1)
    .fill("Câu trả lời B: xác thực danh tính.");
  await page.getByText("Đã lưu trên máy chủ.", { exact: true }).waitFor();
  await page.reload();
  await page.locator("#timer").waitFor();
  assert(
    (await page.locator("[data-exam-answer]").nth(1).inputValue()).includes(
      "Câu trả lời B",
    ),
  );
  await page.locator("#exam-finish").click();
  await page.getByRole("heading", { name: "Báo cáo đối chiếu" }).waitFor();
  await shot(page, "exam");
  const latest = await request("export");
  await request("restore", latest, `http://127.0.0.1:${port + 1}`);
  await request("restore", old, `http://127.0.0.1:${port + 1}`);
  const restored = (
    await request("bootstrap", undefined, `http://127.0.0.1:${port + 1}`)
  ).state;
  assert.equal(restored.exams.length, 1);
  assert(restored.exams[0].finished);
  assert(restored.exams[0].answers["TN1-Q002"].includes("Câu trả lời B"));
  assert.equal(restored.attempts.length, latest.tables.attempts.length);
  await request("exam/finish", { id: oldExam.id });
  assert.equal(
    (await request("export")).tables.attempts.length,
    latest.tables.attempts.length,
  );
  await stop(target);
  passed.push("P0A_new_exam_backup_merge_old_cannot_overwrite_no_duplicate");
  await visit(page, "settings");
  const download = page.waitForEvent("download");
  await page.locator("#export").click();
  await (await download).saveAs(path.join(temp, "learner-backup.json"));
  await page
    .locator("#restore")
    .setInputFiles(path.join(temp, "learner-backup.json"));
  await page
    .getByText("Đã hợp nhất bản sao tiến độ.", { exact: true })
    .waitFor();
  await page.locator("#shift-day").fill("1");
  await page.locator("#shift-date").fill("2027-01-01");
  await page.locator("#shift-all").click();
  await page
    .getByText("Đã dời lịch; lịch sử được giữ nguyên.", { exact: true })
    .waitFor();
  await visit(page, "day/1");
  assert(
    (await page.locator(".calendar-info").innerText()).includes("01/01/2027"),
  );
  assert((await page.locator("#date-range").innerText()).includes("2027"));
  await visit(page, "day/51");
  assert.equal(await page.locator(".qrow").count(), 8);
  assert((await page.locator("main").innerText()).includes("28/80"));
  await shot(page, "final-selective");
  passed.push(
    "backup_UI_restore_and_shift_to_2027_final_eight_global_coverage",
  );
  // Fake clock + queued predeadline save: the server has received the body but
  // its worker cannot commit until the deadline has passed. Browser timer hits zero.
  clock("2026-10-12T10:00:00+00:00");
  const timed = await request("exam/start", { kind: "baseline" });
  clock("2026-10-12T10:44:55+00:00");
  await visit(page, "exam/" + timed.id, "#timer");
  fs.writeFileSync(path.join(data, "gate.json"), "{}");
  await page
    .locator("[data-exam-answer]")
    .first()
    .fill("Ý cuối trước hạn, lưu đang chờ khi đồng hồ về 0.");
  await until(
    () => fs.existsSync(path.join(data, "received.json")),
    "Predeadline request was not received",
  );
  const receipt = JSON.parse(
    fs.readFileSync(path.join(data, "received.json"), "utf8"),
  );
  assert(new Date(receipt.received) < new Date(timed.deadline));
  clock("2026-10-12T10:45:01+00:00");
  await until(
    () =>
      page
        .locator("#timer")
        .innerText()
        .then((t) => t === "00:00"),
    "Timer did not hit zero",
  );
  assert(
    await page
      .locator("[data-exam-answer]")
      .first()
      .evaluate((el) => el.readOnly),
  );
  fs.unlinkSync(path.join(data, "gate.json"));
  await page.getByRole("heading", { name: "Báo cáo đối chiếu" }).waitFor();
  const final = (await request("bootstrap")).state.exams.find(
    (e) => e.id === timed.id,
  );
  assert(final.finished);
  assert(final.answers["TN1-Q032"].includes("Ý cuối trước hạn"));
  const count = (await request("export")).tables.attempts.length;
  await request("exam/save", {
    id: timed.id,
    revision: 99,
    answers: { "TN1-Q032": "Sửa sau deadline" },
  });
  await request("exam/finish", { id: timed.id });
  assert.equal((await request("export")).tables.attempts.length, count);
  assert.deepEqual(
    (await request("bootstrap")).state.exams.find((e) => e.id === timed.id)
      .answers,
    final.answers,
  );
  await page.reload();
  await page.getByRole("heading", { name: "Báo cáo đối chiếu" }).waitFor();
  assert((await page.locator("main").innerText()).includes("Ý cuối trước hạn"));
  await shot(page, "deadline-preserved");
  passed.push(
    "P0B_fake_clock_received_pending_zero_freeze_preserve_reload_idempotent_reject_late",
  );
  // Network failure keeps local recovery text, visibly outside the submitted paper.
  clock("2026-10-12T11:00:00+00:00");
  const offline = await request("exam/start", { kind: "baseline" });
  await visit(page, "exam/" + offline.id, "#timer");
  await page.route("**/api/exam/save", (r) => r.abort());
  await page
    .locator("[data-exam-answer]")
    .first()
    .fill("Nháp mất kết nối phải còn nguyên.");
  await page.getByText(/Chưa lưu lên máy chủ/).waitFor();
  await page.unroute("**/api/exam/save");
  clock("2026-10-12T11:46:00+00:00");
  await page.reload();
  await page
    .getByRole("heading", { name: "Nháp phục hồi · không tính vào bài đã nộp" })
    .waitFor();
  assert(
    (await page.locator("main").innerText()).includes(
      "Nháp mất kết nối phải còn nguyên.",
    ),
  );
  assert.deepEqual(
    (await request("bootstrap")).state.exams.find((e) => e.id === offline.id)
      .answers,
    {},
  );
  passed.push("offline_recovery_kept_separate_from_submitted_answers");
  const beforeRestart = await request("export");
  await stop(serverProcess);
  serverProcess = await start(data, port);
  const afterRestart = await request("export");
  assert.deepEqual(afterRestart.tables, beforeRestart.tables);
  await page.reload();
  await page.getByRole("heading", { name: "Báo cáo đối chiếu" }).waitFor();
  passed.push("server_restart_preserves_all_six_tables");
  for (const route of ["plan", "bank", "day/7", "day/8", "day/51", "settings"])
    await visit(page, route);
  await page.setViewportSize({ width: 390, height: 844 });
  for (const [route, selector, name] of [
    ["day/8", "main h1", "mobile-390"],
    ["math/ecc", "#math-answer", "mobile-ecc"],
    ["diagrams", "#diagram-answer", "mobile-diagram"],
    ["code", "#code-answer", "mobile-code"],
  ]) {
    await visit(page, route, selector);
    await noOverflow(page, route);
    await shot(page, name);
  }
  for (const route of [
    "plan",
    "bank",
    "review",
    "exams",
    "settings",
    "day/51",
  ]) {
    await visit(page, route);
    await noOverflow(page, "mobile-" + route);
  }
  await visit(page, "card/TN1-Q015/8", "#answer");
  await page
    .locator("#answer")
    .fill("MAC dùng nhãn mức và hạng mục để quyết định truy cập theo quy tắc.");
  await page.locator("#reveal").click();
  await page.locator("#grade").waitFor();
  await noOverflow(page, "mobile-card-rubric");
  await shot(page, "mobile-card");
  const mobileExam = await request("exam/start", { kind: "week1" });
  await visit(page, "exam/" + mobileExam.id, "#timer");
  await page
    .locator("[data-exam-answer]")
    .first()
    .fill("Bài thi trên màn hình 390px được lưu.");
  await page.getByText("Đã lưu trên máy chủ.", { exact: true }).waitFor();
  await noOverflow(page, "mobile-active-exam");
  await shot(page, "mobile-exam");
  await page.locator("#exam-finish").click();
  await page.getByRole("heading", { name: "Báo cáo đối chiếu" }).waitFor();
  await noOverflow(page, "mobile-exam-report");
  passed.push("Vietnamese_390_and_1440_no_horizontal_overflow_offline_assets");
  assert.equal(errors.length, 0);
  assert.equal(external.length, 0);
  const report = {
    status: "PASS",
    passed,
    errors,
    external,
    deadline: { receipt, submitted: final.answers, attempt_count: count },
    backup: {
      old_answers: oldExam.answers,
      new_answers: restored.exams[0].answers,
      finished: restored.exams[0].finished,
    },
    restart: { tables_preserved: Object.keys(beforeRestart.tables) },
    screenshots: fs.readdirSync(output).filter((s) => s.endsWith(".png")),
  };
  fs.writeFileSync(
    path.join(output, "browser-report.json"),
    JSON.stringify(report, null, 2),
  );
  console.log(JSON.stringify(report, null, 2));
})()
  .catch((e) => {
    fs.writeFileSync(path.join(output, "failure.txt"), e.stack);
    console.error(e);
    process.exitCode = 1;
  })
  .finally(async () => {
    if (context) await context.close();
    for (const child of processes) await stop(child);
    // Keep the isolated profile/database under the printed temp path for diagnosis.
    console.log("Isolated QA data: " + temp);
  });
