const $ = (id) => document.getElementById(id);
const money = (value) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
const size = (value) => Number(value).toLocaleString('en-US', { maximumFractionDigits: 3 });
let config = null;
let currentPlan = null;
let photoUrls = [];

function node(tag, className, content) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (content !== undefined) element.textContent = content;
  return element;
}

function showMessage(message, type = 'info') {
  const box = $('message');
  box.textContent = message;
  box.className = `message ${type}`;
  box.hidden = false;
}

function clearMessage() { $('message').hidden = true; }

function selectedIdeaId() {
  return document.querySelector('input[name="ideaPreset"]:checked')?.value || null;
}

function chooseIdea(id, focusDescription = true) {
  const preset = config.ideas[id];
  if (!preset) return;
  const description = $('description-step');
  if (description.dataset.ideaPreset !== id) $('idea').value = '';
  description.dataset.ideaPreset = id;
  description.hidden = false;
  $('length').value = preset.length;
  $('width').value = preset.width;
  $('idea-prompt').textContent = `${preset.title} starts at ${preset.length} × ${preset.width} in. Describe your preferences, then confirm the final measurements below.`;
  if (focusDescription) $('idea').focus();
}

function renderIdeas() {
  const list = $('idea-options');
  list.replaceChildren();
  Object.entries(config.ideas).forEach(([id, preset]) => {
    const option = node('label', 'idea-option');
    const input = node('input');
    input.type = 'radio'; input.name = 'ideaPreset'; input.value = id; input.required = true;
    const copy = node('span');
    copy.append(node('strong', '', preset.title), node('small', '', preset.summary), node('em', '', `${preset.length} × ${preset.width} in · 30 in high`));
    option.append(input, copy);
    list.append(option);
  });
  list.addEventListener('change', (event) => {
    if (event.target.name === 'ideaPreset') chooseIdea(event.target.value);
  });
}

function markChanged(event) {
  if (event.target.id === 'confirmed') return;
  if (currentPlan) {
    currentPlan = null;
    $('plan').hidden = true;
    $('empty-state').hidden = false;
    $('empty-state').querySelector('h3').textContent = 'Your inputs changed.';
    $('empty-state').querySelector('p').textContent = 'Review and regenerate to see one consistent new plan.';
    $('print-button').hidden = true;
  }
  if (event.target.name === 'mode') return;
  $('confirmed').checked = false;
  $('review-panel').hidden = true;
}

function renderTools() {
  const list = $('tool-list');
  Object.entries(config.tools).forEach(([key, label]) => {
    const row = node('label', 'check-item');
    const input = node('input');
    input.type = 'checkbox'; input.name = 'tools'; input.value = key;
    const text = node('span', '', label);
    row.append(input, text); list.append(row);
  });
}

function addInventoryRow(defaults = {}) {
  const row = node('div', 'inventory-row');
  const top = node('div', 'inventory-row-top');
  const select = node('select'); select.setAttribute('aria-label', 'Owned item type');
  Object.entries(config.catalog).forEach(([sku, item]) => {
    const option = node('option', '', item.label); option.value = sku; select.append(option);
  });
  select.value = defaults.sku || 'leg_stock';
  const remove = node('button', 'remove-button', 'Remove'); remove.type = 'button';
  remove.addEventListener('click', () => { row.remove(); markChanged({ target: row }); });
  top.append(select, remove);
  const quantityLabel = node('label', 'inventory-qty', 'Quantity owned');
  const quantity = node('input'); quantity.type = 'number'; quantity.min = '1'; quantity.max = '1000'; quantity.step = '1'; quantity.value = defaults.quantity || '1'; quantity.setAttribute('aria-label', 'Quantity owned');
  quantityLabel.append(quantity);
  const dimensions = node('div', 'inventory-dimensions');
  const fields = {};
  [['length', 'Length'], ['width', 'Width'], ['thickness', 'Thickness']].forEach(([key, label]) => {
    const wrap = node('label', '', `${label} (in)`);
    const input = node('input'); input.type = 'number'; input.min = '0.1'; input.max = '200'; input.step = '0.001'; input.setAttribute('aria-label', `Actual ${label.toLowerCase()}`);
    wrap.append(input); dimensions.append(wrap); fields[key] = input;
  });
  const confirmation = node('label', 'inventory-confirm');
  const check = node('input'); check.type = 'checkbox'; check.checked = defaults.confirmed || false;
  confirmation.append(check, node('span', '', 'I measured this stock / counted these parts'));
  function updateKind(reset = false) {
    const item = config.catalog[select.value];
    dimensions.hidden = item.kind !== 'lumber';
    if (reset || defaults.sku) {
      for (const key of Object.keys(fields)) fields[key].value = defaults[key] ?? item[key] ?? '';
    }
  }
  select.addEventListener('change', () => updateKind(true));
  updateKind(true);
  row.append(top, quantityLabel, dimensions, confirmation);
  row.read = () => ({ sku: select.value, quantity: quantity.value, confirmed: check.checked,
    length: fields.length.value, width: fields.width.value, thickness: fields.thickness.value });
  $('inventory-rows').append(row);
  return row;
}

function payload() {
  return {
    ideaPreset: selectedIdeaId(), idea: $('idea').value.trim(), length: $('length').value, width: $('width').value, budget: $('budget').value,
    skill: document.querySelector('input[name="skill"]:checked').value,
    tools: [...document.querySelectorAll('input[name="tools"]:checked')].map((input) => input.value),
    inventory: [...document.querySelectorAll('.inventory-row')].map((row) => row.read()),
    inventoryNotes: $('inventory-notes').value.trim(),
    confirmed: $('confirmed').checked,
    mode: document.querySelector('input[name="mode"]:checked').value,
  };
}

function review() {
  clearMessage();
  const data = payload();
  if (!data.ideaPreset) { showMessage('Choose a starting table idea first.', 'error'); $('idea-options').querySelector('input')?.focus(); return; }
  if (!data.idea) { showMessage('Describe your table idea first.', 'error'); $('idea').focus(); return; }
  if (!Number.isFinite(Number(data.length)) || data.length === '' || Number(data.length) < 48 || Number(data.length) > 72 || Number(data.length) * 4 % 1 !== 0) {
    showMessage('Enter a table length from 48 to 72 inches in quarter-inch increments.', 'error'); $('length').focus(); return;
  }
  if (!Number.isFinite(Number(data.width)) || data.width === '' || Number(data.width) < 28 || Number(data.width) > 40 || Number(data.width) * 4 % 1 !== 0) {
    showMessage('Enter a table width from 28 to 40 inches in quarter-inch increments.', 'error'); $('width').focus(); return;
  }
  if (data.budget === '' || !Number.isFinite(Number(data.budget)) || Number(data.budget) < 0) {
    showMessage('Enter your budget in US dollars.', 'error'); $('budget').focus(); return;
  }
  const summary = $('summary'); summary.replaceChildren();
  const facts = [
    ['Starting idea', config.ideas[data.ideaPreset].title], ['Description', data.idea], ['Table size', `${size(data.length)} × ${size(data.width)} × 30 in`],
    ['Budget', money(Number(data.budget))], ['Instruction detail', data.skill],
    ['Tools selected', `${data.tools.length} of ${Object.keys(config.tools).length}`],
    ['Owned material entries', String(data.inventory.length)],
    ['Reference photos', String($('reference-photos').files.length)],
  ];
  for (const [label, value] of facts) { const row = node('div', 'summary-row'); row.append(node('span', '', label), node('strong', '', value)); summary.append(row); }
  $('confirmed').checked = false;
  $('review-panel').hidden = false;
  $('review-panel').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function photoPreview() {
  photoUrls.forEach((url) => URL.revokeObjectURL(url)); photoUrls = [];
  const container = $('photo-previews'); container.replaceChildren();
  const files = [...$('reference-photos').files].slice(0, 6);
  files.forEach((file) => {
    if (!file.type.startsWith('image/')) return;
    const url = URL.createObjectURL(file); photoUrls.push(url);
    const figure = node('figure'); const img = node('img'); img.src = url; img.alt = `Reference photo: ${file.name}`;
    figure.append(img, node('figcaption', '', file.name)); container.append(figure);
  });
  $('photo-note').textContent = files.length
    ? `${files.length} reference photo${files.length === 1 ? '' : 's'} attached in this browser only. Confirm dimensions in the item rows; photos are not measured or uploaded.`
    : 'Photos stay in this browser session. They are not measured or identified by the app.';
}

function svg(tag, attrs = {}, text) {
  const element = document.createElementNS('http://www.w3.org/2000/svg', tag);
  Object.entries(attrs).forEach(([key, value]) => element.setAttribute(key, String(value)));
  if (text !== undefined) element.textContent = text;
  return element;
}

function drawDiagram(plan) {
  const root = $('diagram'); root.replaceChildren();
  const g = plan.geometry, scale = 4.05, tx = 80, ty = 84, tw = g.length * scale, th = g.width * scale;
  const fx = 460, fy = 278, fw = tw, fh = g.height * scale;
  function add(tag, attrs, text) { const element = svg(tag, attrs, text); root.append(element); return element; }
  function label(x, y, text, klass = 'svg-label', anchor = 'middle') { add('text', { x, y, 'text-anchor': anchor, class: klass }, text); }
  function line(x1, y1, x2, y2, klass = 'svg-line') { add('line', { x1, y1, x2, y2, class: klass }); }
  function dimension(x1, y1, x2, y2, text, vertical = false) {
    line(x1, y1, x2, y2, 'svg-dimension');
    if (vertical) { line(x1 - 5, y1, x1 + 5, y1, 'svg-dimension'); line(x2 - 5, y2, x2 + 5, y2, 'svg-dimension'); label(x1 - 10, (y1 + y2) / 2, text, 'svg-dim-text', 'end'); }
    else { line(x1, y1 - 5, x1, y1 + 5, 'svg-dimension'); line(x2, y2 - 5, x2, y2 + 5, 'svg-dimension'); label((x1 + x2) / 2, y1 - 9, text, 'svg-dim-text'); }
  }
  label(tx, 28, 'TOP VIEW', 'svg-view-title', 'start');
  add('rect', { x: tx, y: ty, width: tw, height: th, rx: 3, class: 'svg-top' });
  label(tx + tw / 2, ty + th / 2 + 4, 'T1', 'svg-top-id');
  const leg = g.legSize * scale, inset = g.overhang * scale;
  const positions = [[tx + inset, ty + inset, 'L1'], [tx + tw - inset - leg, ty + inset, 'L2'], [tx + inset, ty + th - inset - leg, 'L3'], [tx + tw - inset - leg, ty + th - inset - leg, 'L4']];
  const left = tx + inset + leg, right = tx + tw - inset - leg, top = ty + inset + leg, bottom = ty + th - inset - leg;
  add('rect', { x: left, y: ty + inset + leg / 2 - 3, width: right - left, height: 6, class: 'svg-apron' });
  add('rect', { x: left, y: ty + th - inset - leg / 2 - 3, width: right - left, height: 6, class: 'svg-apron' });
  add('rect', { x: tx + inset + leg / 2 - 3, y: top, width: 6, height: bottom - top, class: 'svg-apron' });
  add('rect', { x: tx + tw - inset - leg / 2 - 3, y: top, width: 6, height: bottom - top, class: 'svg-apron' });
  positions.forEach(([x, y, id]) => { add('rect', { x, y, width: leg, height: leg, class: 'svg-leg' }); label(x + leg / 2, y + leg / 2 + 3, id, 'svg-leg-id'); });
  label(tx + tw / 2, ty + inset + leg + 17, 'A1', 'svg-part-id');
  label(tx + tw / 2, ty + th - inset - leg - 9, 'A2', 'svg-part-id');
  label(tx + inset + leg + 18, ty + th / 2 - 12, 'B1', 'svg-part-id');
  label(tx + tw - inset - leg - 18, ty + th / 2 - 12, 'B2', 'svg-part-id');
  dimension(tx, ty - 27, tx + tw, ty - 27, `${size(g.length)} in`);
  dimension(tx - 27, ty, tx - 27, ty + th, `${size(g.width)} in`, true);

  label(fx, 235, 'FRONT ELEVATION', 'svg-view-title', 'start');
  add('rect', { x: fx, y: fy, width: fw, height: Math.max(4, g.height * scale / 40), class: 'svg-top' });
  const legY = fy + 4, legH = fh - 4;
  add('rect', { x: fx + inset, y: legY, width: leg, height: legH, class: 'svg-leg' });
  add('rect', { x: fx + fw - inset - leg, y: legY, width: leg, height: legH, class: 'svg-leg' });
  add('rect', { x: fx + inset + leg, y: legY + 4, width: fw - 2 * (inset + leg), height: g.apronDepth * scale, class: 'svg-apron-front' });
  label(fx + fw / 2, legY + 15, 'A1', 'svg-part-id');
  label(fx + inset + leg / 2, fy + fh - 10, 'L1', 'svg-leg-id');
  label(fx + fw - inset - leg / 2, fy + fh - 10, 'L2', 'svg-leg-id');
  label(fx + fw / 2, fy - 8, 'T1', 'svg-part-id');
  dimension(fx + fw + 17, fy, fx + fw + 17, fy + fh, `${size(g.height)} in`, true);
}

function renderCutList(plan) {
  const grouped = new Map();
  plan.parts.forEach((part) => {
    const key = [part.label, part.length, part.width, part.thickness].join('|');
    if (!grouped.has(key)) grouped.set(key, { ...part, ids: [] });
    grouped.get(key).ids.push(part.id);
  });
  const body = $('cut-rows'); body.replaceChildren();
  for (const group of grouped.values()) {
    const tr = node('tr');
    [group.ids.join(', '), group.label, `${size(group.length)} × ${size(group.width)} × ${size(group.thickness)}`, String(group.ids.length)]
      .forEach((value) => tr.append(node('td', '', value)));
    body.append(tr);
  }
  $('stock-note').textContent = `Stock assignment uses a ${size(plan.policy.kerf)} in saw kerf per crosscut. ${plan.policy.stockRule}`;
  const cards = $('stock-cards'); cards.replaceChildren();
  for (const [sku, bins] of Object.entries(plan.stockAssignment)) {
    const card = node('div', 'stock-card');
    card.append(node('strong', '', `${config.catalog[sku].label} · ${bins.length} unit${bins.length === 1 ? '' : 's'}`));
    bins.forEach((bin, index) => card.append(node('p', '', `Unit ${index + 1}: ${bin.partIds.join(', ')}${bin.remaining === null ? '' : ` · ${size(bin.remaining)} in remains`}`)));
    cards.append(card);
  }
}

function renderShopping(plan) {
  const body = $('shopping-rows'); body.replaceChildren();
  plan.shopping.forEach((item) => {
    const tr = node('tr');
    [item.label, String(item.needed), String(item.ownedUsed), `${item.toBuy} ${item.purchaseUnit}`, money(item.cost)]
      .forEach((value) => tr.append(node('td', '', value)));
    body.append(tr);
  });
  $('total').textContent = money(plan.estimate.purchaseSubtotal);
  $('estimate-note').textContent = `${plan.estimate.priceSource} (${plan.estimate.priceDate}). ${plan.estimate.exclusions}`;
  const feedback = $('inventory-feedback'); feedback.replaceChildren();
  const ignored = plan.inventory.filter((entry) => !entry.matching);
  if (ignored.length) {
    const box = node('div', 'inventory-feedback'); box.append(node('strong', '', 'Owned items not counted'));
    ignored.forEach((entry) => box.append(node('p', '', `${entry.quantity} × ${entry.label}: ${entry.reason}`)));
    feedback.append(box);
  }
  const banner = $('budget-banner');
  banner.hidden = !plan.estimate.overBudget;
  if (plan.estimate.overBudget) banner.textContent = `This sample purchase estimate is ${money(plan.estimate.purchaseSubtotal - plan.estimate.budget)} over your ${money(plan.estimate.budget)} budget. Revise the size, budget, or confirmed materials before building.`;
}

function renderSteps(plan) {
  const list = $('steps'); list.replaceChildren();
  plan.steps.forEach((step, index) => {
    const li = node('li', 'step');
    const head = node('div', 'step-head'); head.append(node('span', 'step-number', String(index + 1).padStart(2, '0')), node('h4', '', step.title));
    li.append(head, node('p', 'step-action', step.action), node('p', 'step-detail', step.detail));
    const meta = node('div', 'step-meta');
    meta.append(node('p', '', `Parts: ${step.partIds.join(', ')}`), node('p', '', `Tools: ${step.tools.map((id) => config.tools[id]).join(', ')}`));
    li.append(meta, node('p', 'step-check', `Check: ${step.check}`), node('p', 'step-safety', `Safety: ${step.safety}`));
    list.append(li);
  });
  const ai = $('ai-note'); ai.replaceChildren();
  ai.append(node('strong', '', plan.ai.source === 'Sample preview' ? 'Sample mode' : `OCI guidance · ${plan.ai.model}`), node('p', '', plan.ai.text));
}

function renderPlan(plan) {
  currentPlan = plan;
  $('empty-state').hidden = true;
  $('plan').hidden = false;
  $('print-button').hidden = false;
  $('prototype-notice').textContent = plan.prototypeNotice;
  $('plan-mode').textContent = `${plan.ai.source.toUpperCase()} / ${plan.templateId}`;
  $('plan-idea-title').textContent = plan.inputs.ideaTitle;
  $('plan-subtitle').textContent = `A fixed-height rectangular table for an indoor dining space. ${plan.inputs.skill === 'beginner' ? 'Beginner' : 'Intermediate'} instruction detail.`;
  $('revision').textContent = `REV ${plan.revision}`;
  $('footer-revision').textContent = plan.revision;
  $('plan-meta').textContent = `${plan.inputs.ideaTitle} · ${size(plan.inputs.length)} × ${size(plan.inputs.width)} × ${size(plan.inputs.height)} in · Revision ${plan.revision}`;
  const metrics = $('metrics'); metrics.replaceChildren();
  [['Length', `${size(plan.inputs.length)} in`], ['Width', `${size(plan.inputs.width)} in`], ['Height', `${size(plan.inputs.height)} in`], ['Est. buy', money(plan.estimate.purchaseSubtotal)]]
    .forEach(([label, value]) => { const card = node('div', 'metric'); card.append(node('span', '', label), node('strong', '', value)); metrics.append(card); });
  drawDiagram(plan); renderCutList(plan); renderShopping(plan); renderSteps(plan);
  const tools = $('tool-result'); tools.replaceChildren();
  plan.tools.forEach((tool) => tools.append(node('li', '', `✓ ${tool.label}`)));
  $('plan').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function generate(event) {
  event.preventDefault(); clearMessage();
  const data = payload();
  if (!data.confirmed) { showMessage('Confirm the reviewed inputs before generating.', 'error'); return; }
  const button = $('generate-button'); button.disabled = true; button.textContent = 'Building the plan…';
  try {
    const response = await fetch('/api/plan', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Plan generation failed.');
    renderPlan(result);
    showMessage(result.ai.source === 'Sample preview' ? 'Sample preview ready. No live OCI request was made.' : 'Plan ready. OCI returned a live explanation.', 'success');
  } catch (error) {
    showMessage(`${error.message} Your inputs are still here. Correct the issue and retry.`, 'error');
  } finally {
    button.disabled = false; button.replaceChildren(document.createTextNode('Generate table plan '), node('span', '', '↗'));
  }
}

async function init() {
  try {
    const response = await fetch('/api/config');
    if (!response.ok) throw new Error('Configuration unavailable.');
    config = await response.json();
    renderIdeas();
    renderTools();
    const live = document.querySelector('input[name="mode"][value="oci"]');
    live.disabled = !config.configured;
    if (config.configured) live.checked = true;
    $('oci-status').textContent = config.configured
      ? `Live OCI available · ${config.model} in ${config.region}. The key stays on the server.`
      : 'Live OCI needs OCI_GENAI_API_KEY on the server. Sample preview remains available.';
  } catch (error) { showMessage('The local app could not load its catalog. Restart the server and refresh.', 'error'); return; }
  $('add-inventory').addEventListener('click', () => { addInventoryRow(); markChanged({ target: $('inventory-rows') }); });
  $('review-button').addEventListener('click', review);
  $('planner-form').addEventListener('submit', generate);
  $('planner-form').addEventListener('input', markChanged);
  $('planner-form').addEventListener('change', markChanged);
  $('reference-photos').addEventListener('change', photoPreview);
  $('print-button').addEventListener('click', () => window.print());
  $('sample-button').addEventListener('click', () => {
    document.querySelector('input[name="ideaPreset"][value="everyday"]').checked = true;
    chooseIdea('everyday', false);
    $('idea').value = 'I want a simple indoor dining table for four, and I already have one 4×4 board.';
    $('length').value = '60'; $('width').value = '32'; $('budget').value = '220';
    document.querySelectorAll('input[name="tools"]').forEach((input) => { input.checked = true; });
    document.querySelector('input[name="skill"][value="beginner"]').checked = true;
    $('inventory-notes').value = 'One sound 8 ft 4×4 board, measured at 3.5 × 3.5 in.';
    $('inventory-rows').replaceChildren();
    addInventoryRow({ sku: 'leg_stock', quantity: 1, length: 96, width: 3.5, thickness: 3.5, confirmed: true });
    markChanged({ target: $('idea') }); review();
  });
}

init();
