#!/usr/bin/env python3
"""Render a standalone interactive portfolio dashboard from reconciled JSON."""

import argparse
import json
import sys
from pathlib import Path

from validate_dashboard_input import load, presentation_state, validate


TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Portfolio Performance Dashboard</title>
<style>
:root{color-scheme:dark;--bg:#0a0f16;--shell:#101720;--panel:#171f2b;--panel2:#202938;--line:#2b3647;--text:#eef2f8;--muted:#eef2f8;--accent:#91a7ff;--accent2:#222e59;--on-accent:#101720;--good:#55d6aa;--bad:#ff8585;--warn:#f7b955;--shadow:0 18px 60px rgba(0,0,0,.28)}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.45 Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;padding:28px}button,select,input{font:inherit}button{cursor:pointer}.app{max-width:1240px;margin:auto;background:var(--shell);border:1px solid var(--line);border-radius:24px;overflow:hidden;box-shadow:var(--shadow)}
.head{display:flex;align-items:center;justify-content:space-between;gap:20px;padding:24px 28px;background:var(--panel);border-bottom:1px solid var(--line)}.company{display:flex;align-items:center;gap:14px}.logo{width:46px;height:46px;border-radius:14px;background:var(--accent);color:var(--on-accent);display:grid;place-items:center;font-weight:750;font-size:18px}.head h1{font-size:21px;margin:0 0 2px}.sub,.muted{color:var(--text);font-weight:500}.badge{display:inline-flex;padding:5px 9px;border-radius:99px;background:var(--accent2);color:var(--accent);font-size:12px;font-weight:650}.synthetic,#quality{background:transparent;color:var(--warn)}.warn{color:var(--warn)}.share{border:1px solid var(--accent);border-radius:10px;padding:8px 11px;background:transparent;color:var(--accent);font-weight:650}.share:hover{background:var(--accent2)}
.body{padding:22px 28px 28px}.toolbar{display:flex;align-items:end;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:18px}.filters{display:flex;align-items:end;gap:12px;flex-wrap:wrap}.field{display:grid;gap:6px;color:var(--text);font-weight:500}select{min-width:155px;padding:10px 34px 10px 11px;color:var(--text);background:var(--panel);border:1px solid var(--line);border-radius:11px;font-weight:500}select option{color:var(--text);background:var(--panel)}.check{min-height:42px;display:flex;align-items:center;gap:8px;color:var(--text);font-weight:500}.check input{width:18px;height:18px;accent-color:var(--accent)}.tabs{display:flex;gap:4px;padding:4px;background:var(--panel2);border-radius:12px}.tab{border:0;border-radius:9px;padding:9px 13px;color:var(--text);background:transparent;font-weight:500}.tab.active{color:var(--text);background:var(--panel);box-shadow:0 0 0 1px var(--line)}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:18px}.stat,.pane,.state{background:var(--panel);border:1px solid var(--line);border-radius:18px}.stat{padding:16px}.stat-top{display:flex;justify-content:space-between;gap:10px;color:var(--muted)}.big{font-size:27px;font-weight:550;margin:9px 0 2px;font-variant-numeric:tabular-nums}.good{color:var(--good)}.bad{color:var(--bad)}
.workspace{display:grid;grid-template-columns:minmax(0,1.65fr) minmax(300px,.82fr);gap:16px;align-items:start}.pane{overflow:hidden}.pane-head{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:15px 17px;border-bottom:1px solid var(--line)}.pane-head h2{font-size:16px;margin:0}.rows{padding:8px 17px 11px}.row{width:100%;display:grid;grid-template-columns:190px minmax(120px,1fr) 80px;gap:12px;align-items:center;border:0;border-bottom:1px solid var(--line);background:transparent;color:var(--text);padding:11px 0;text-align:left}.row:last-child{border-bottom:0}.row:hover .name,.row.selected .name{color:var(--accent)}.track{position:relative;height:10px;border-radius:99px;background:var(--panel2);overflow:hidden}.track:after{content:"";position:absolute;left:50%;top:0;bottom:0;width:1px;background:var(--line)}.bar{position:absolute;top:2px;bottom:2px;border-radius:99px;min-width:2px}.bar.neg{right:50%;background:var(--bad)}.bar.pos{left:50%;background:var(--good)}.num{text-align:right;font-variant-numeric:tabular-nums}
.detail{padding:18px}.detail-title{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:16px}.detail-title h3{margin:0;font-size:18px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:10px}.box{padding:12px;border-radius:12px;background:var(--panel2)}.box span{display:block;color:var(--text);font-weight:500;margin-bottom:5px}.box strong{font-size:17px}.rule{height:1px;background:var(--line);margin:17px 0}.kicker{text-transform:uppercase;letter-spacing:.08em;color:var(--text);font-size:12px;font-weight:500}.callout{border-left:3px solid var(--warn);background:var(--panel2);padding:11px 12px}.ask{width:100%;padding:10px 12px;border:1px solid var(--accent);border-radius:11px;background:transparent;color:var(--accent);font-weight:650}.ask:hover{background:var(--accent2)}.list{list-style:none;margin:0;padding:8px 17px 17px}.list li{padding:13px 0;border-bottom:1px solid var(--line)}.list li:last-child{border:0}.list strong{display:block;margin-bottom:3px}.share-panel{position:fixed;inset:0;z-index:2;display:grid;place-items:center;padding:20px;background:rgba(0,0,0,.55)}.share-panel[hidden]{display:none}.share-dialog{width:min(460px,100%);padding:22px;border:1px solid var(--line);border-radius:18px;background:var(--panel);box-shadow:var(--shadow)}.share-dialog h2{margin:0 0 8px;font-size:18px}.share-dialog p{margin:0 0 16px}.share-dialog input{width:100%;padding:10px 11px;color:var(--text);background:var(--shell);border:1px solid var(--line);border-radius:10px}.share-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:16px}.share-cancel,.share-submit{border-radius:10px;padding:9px 12px;font-weight:650}.share-cancel{border:1px solid var(--line);background:transparent;color:var(--text)}.share-submit{border:1px solid var(--accent);background:var(--accent);color:var(--on-accent)}.toast{position:fixed;right:20px;bottom:20px;padding:11px 14px;border-radius:11px;background:var(--text);color:var(--shell);box-shadow:var(--shadow);visibility:hidden;transform:translateY(8px);transition:.2s;pointer-events:none}.toast.show{visibility:visible;transform:none}.state{padding:26px}.state h2{margin:0 0 7px}.errors{margin:16px 0 0;padding-left:20px}.errors li+li{margin-top:7px}
@media(max-width:760px){body{padding:0}.app{border-radius:0;border-left:0;border-right:0}.head,.body{padding:18px}.stats,.workspace{grid-template-columns:1fr}.toolbar{align-items:stretch}.tabs{width:100%}.tab{flex:1}.row{grid-template-columns:120px 1fr 66px;gap:8px}.synthetic{display:none}}
</style>
</head>
<body>
<div class="app">
  <header class="head"><div class="company"><div class="logo" id="logo">P</div><div><h1 id="company">Portfolio review</h1><div class="sub" id="period"></div></div></div><div>__SHARE_HEADER__<span class="badge synthetic" id="synthetic" hidden>Synthetic demonstration</span> <span class="badge" id="quality"></span></div></header>
  <div class="body"><div id="app"></div></div>
</div>
__SHARE_PANEL__
<div class="toast" id="toast" role="status" aria-live="polite">Prompt copied</div>
<script>
const DATA=__PAYLOAD__;
const IS_BLEND_EXPORT=__BLEND_EXPORT__;
const STATE=__STATE__;
const LABELS={budget:'Budget',prior_month:'Prior month',prior_year:'Prior year',current_forecast:'Current forecast',original_investment_case:'Investment case'};
const ui={group:'all',baseline:'budget',material:false,tab:'overview',selected:null};
const app=document.getElementById('app');
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
function fmtValue(v,item){if(v===null||v===undefined)return '—';if(item.unit==='%')return `${Number(v).toFixed(1)}%`;if(item.unit==='USDm')return `${item.currency||'USD'} ${Number(v).toFixed(1)}m`;if(item.unit==='USD')return `${item.currency||'USD'} ${Number(v).toFixed(1)}`;return `${Number(v).toLocaleString()}${item.unit?' '+item.unit:''}`}
function comparison(k){return k.comparisons[ui.baseline]}
function delta(k){const c=comparison(k);if(!c)return 'Unavailable';if(k.unit==='%'&&c.basis_point_difference!==undefined)return `${c.basis_point_difference>=0?'+':''}${Number(c.basis_point_difference).toFixed(0)} bps`;if(c.percentage_variance==='not_meaningful')return `${Number(c.absolute_variance)>=0?'+':''}${Number(c.absolute_variance).toFixed(1)} · % not meaningful`;return `${Number(c.percentage_variance)>=0?'+':''}${Number(c.percentage_variance).toFixed(1)}%`}
function tone(k){const c=comparison(k);return !c?'muted':c.favorability==='favorable'?'good':c.favorability==='unfavorable'?'bad':'muted'}
function filtered(){return DATA.results.filter(k=>(ui.group==='all'||k.kpi_type===ui.group)&&(!ui.material||comparison(k)?.materiality==='material'))}
function controls(){return `<div class="toolbar"><div class="filters"><label class="field">KPI group<select id="group"><option value="all">All KPIs</option><option value="financial">Financial</option><option value="operational">Operational</option></select></label><label class="field">Comparison<select id="baseline">${Object.entries(LABELS).map(([v,l])=>`<option value="${v}">${l}</option>`).join('')}</select></label><label class="check"><input id="material" type="checkbox"> Material only</label></div><div class="tabs">${['overview','questions','actions'].map(t=>`<button class="tab ${ui.tab===t?'active':''}" data-tab="${t}">${t[0].toUpperCase()+t.slice(1)}</button>`).join('')}</div></div>`}
function stat(k){return `<div class="stat"><div class="stat-top"><span>${esc(k.kpi)}</span><span>vs ${LABELS[ui.baseline].toLowerCase()}</span></div><div class="big">${esc(fmtValue(k.actual,k))}</div><div class="${tone(k)}">${esc(delta(k))} · ${comparison(k)?.materiality?.replace('_',' ')||'not assessable'}</div></div>`}
function promptFor(k){const c=comparison(k);return `Investigate ${k.kpi} for ${DATA.company}, ${DATA.period}, using only the reconciled results. Actual: ${fmtValue(k.actual,k)}. ${LABELS[ui.baseline]}: ${c?fmtValue(c.comparison,k):'unavailable'}. Variance: ${delta(k)}. Materiality: ${c?.materiality||'not assessable'}. Favorability: ${c?.favorability||'not assessable'}. Evidence class: ${k.evidence_class}. Driver: ${k.management_driver||'Driver not provided; management input required.'}. Evidence source: ${k.evidence_source||'Not supplied'}. Action: ${k.management_action||'Not supplied'}; owner: ${k.action_owner||'Not supplied'}; date: ${k.expected_completion_date||'Not supplied'}. Distinguish facts from missing or contradictory evidence, identify exact management follow-ups, and do not invent facts or make an investment recommendation.`}
function detail(k){const c=comparison(k);return `<aside class="pane"><div class="pane-head"><h2>KPI detail</h2><span class="muted">Select any row</span></div><div class="detail"><div class="detail-title"><h3>${esc(k.kpi)}</h3><span class="badge">${esc(k.evidence_class)}</span></div><div class="pair"><div class="box"><span>Actual</span><strong>${esc(fmtValue(k.actual,k))}</strong></div><div class="box"><span>${LABELS[ui.baseline]}</span><strong>${c?esc(fmtValue(c.comparison,k)):'—'}</strong></div></div><div class="rule"></div><p class="kicker">Evidence-backed commentary</p><p>${esc(k.management_driver||'Driver not provided; management input required.')}</p><p class="callout">${esc(k.evidence_class==='contradictory_evidence'?'Management explanation conflicts with the calculated direction and requires clarification.':k.evidence_class==='missing_evidence'?'Management input is required before attributing this movement.':'Review the supplied evidence and follow-up action.')}</p>${IS_BLEND_EXPORT?'':`<button class="ask" data-ask="${esc(k.kpi)}">Copy investigation request</button>`}</div></aside>`}
function overview(){const list=filtered();if(!list.some(k=>k.kpi===ui.selected))ui.selected=list[0]?.kpi||null;const selected=list.find(k=>k.kpi===ui.selected);const ranked=[...DATA.results].sort((a,b)=>Math.abs(Number(comparison(b)?.percentage_variance)||0)-Math.abs(Number(comparison(a)?.percentage_variance)||0)).slice(0,3);const max=Math.max(1,...list.map(k=>Math.abs(Number(comparison(k)?.percentage_variance)||0)));return `<div class="stats">${ranked.map(stat).join('')}</div><div class="workspace"><section class="pane"><div class="pane-head"><h2>Variance to ${LABELS[ui.baseline].toLowerCase()}</h2><span class="muted">${list.length} KPIs</span></div><div class="rows">${list.length?list.map(k=>{const c=comparison(k),v=Number(c?.percentage_variance)||0,w=Math.max(1,Math.abs(v)/max*48);return `<button class="row ${k.kpi===ui.selected?'selected':''}" data-kpi="${esc(k.kpi)}"><span class="name">${esc(k.kpi)}</span><span class="track"><span class="bar ${v<0?'neg':'pos'}" style="width:${w}%"></span></span><span class="num ${tone(k)}">${esc(delta(k))}</span></button>`}).join(''):'<p class="muted">No KPIs match these filters.</p>'}</div></section>${selected?detail(selected):''}</div>`}
function questions(){const list=filtered().filter(k=>comparison(k)?.materiality==='material'||k.evidence_class.includes('evidence'));return `<section class="pane"><div class="pane-head"><h2>Questions for management</h2><span class="muted">${list.length} open items</span></div><ul class="list">${list.map(k=>`<li><strong>${esc(k.kpi)}</strong><span class="muted">${esc(k.evidence_class==='missing_evidence'?'What explains this material movement, with quantified evidence?':k.evidence_class==='contradictory_evidence'?'Reconcile management commentary with the calculated result.':'Confirm the quantified driver, owner and timing.')}</span></li>`).join('')}</ul></section>`}
function actions(){const list=filtered().filter(k=>k.management_action);return `<section class="pane"><div class="pane-head"><h2>Supported follow-up actions</h2><span class="muted">${list.length} actions</span></div><ul class="list">${list.map(k=>`<li><strong>${esc(k.kpi)} · ${esc(k.management_action)}</strong><span class="muted">${esc(k.action_owner||'Owner not supplied')} · ${esc(k.expected_completion_date||'Date not supplied')}</span></li>`).join('')}</ul></section>`}
function renderNormal(){app.innerHTML=controls()+(ui.tab==='overview'?overview():ui.tab==='questions'?questions():actions());document.getElementById('group').value=ui.group;document.getElementById('baseline').value=ui.baseline;document.getElementById('material').checked=ui.material}
function renderState(){const validation=DATA.validation||{},recon=DATA.reconciliation||{};let title='Dashboard unavailable',copy='The input could not be presented safely.',items=[];if(STATE==='blocked'){title='Source validation failed';copy='Correct the source data and rerun the analysis.';items=validation.errors||[]}else if(STATE==='empty'){title='No data for this period';copy=`No KPI rows were found for ${DATA.period}. Select a populated period or update the source.`}else if(STATE==='reconciliation_failed'){title='Reconciliation failed';copy='Unverified KPI values are hidden until the mismatches are resolved.';items=recon.mismatches||[]}app.innerHTML=`<section class="state"><h2>${esc(title)}</h2><p class="muted">${esc(copy)}</p>${items.length?`<ul class="errors">${items.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`:''}</section>`}
function render(){if(STATE==='ready'||STATE==='warning')renderNormal();else renderState()}
document.getElementById('company').textContent=DATA.company||'Portfolio review';document.getElementById('period').textContent=`Monthly portfolio performance · ${DATA.period||'period unavailable'}`;document.getElementById('logo').textContent=(DATA.company||'P').slice(0,1).toUpperCase();document.getElementById('synthetic').hidden=!DATA.synthetic;document.getElementById('quality').textContent=STATE==='warning'?`${DATA.validation.warnings.length} warnings`:STATE.replace('_',' ');
document.addEventListener('change',e=>{if(e.target.id==='group')ui.group=e.target.value;if(e.target.id==='baseline')ui.baseline=e.target.value;if(e.target.id==='material')ui.material=e.target.checked;render()});
const toast=document.getElementById('toast'),showToast=(message)=>{toast.textContent=message;toast.classList.add('show');setTimeout(()=>{toast.classList.remove('show');toast.textContent='Prompt copied'},2800)};
__SHARE_SCRIPT__
document.addEventListener('click',async e=>{const tab=e.target.closest('[data-tab]');if(tab){ui.tab=tab.dataset.tab;render();return}const row=e.target.closest('[data-kpi]');if(row){ui.selected=row.dataset.kpi;render();return}const ask=e.target.closest('[data-ask]');if(ask){const k=DATA.results.find(x=>x.kpi===ask.dataset.ask);const prompt=promptFor(k);try{await navigator.clipboard.writeText(prompt)}catch{const area=document.createElement('textarea');area.value=prompt;document.body.appendChild(area);area.select();document.execCommand('copy');area.remove()}showToast('Prompt copied')}});
render();
</script>
</body>
</html>'''


def render(payload, state, *, blend_export=False):
    safe_payload = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    share_header = '' if blend_export else '<button class="share" id="share-blend" type="button">Share on Blend</button> '
    share_panel = '' if blend_export else '''<div class="share-panel" id="share-panel" role="dialog" aria-modal="true" aria-labelledby="share-title" hidden><div class="share-dialog"><h2 id="share-title">Share on Blend</h2><p class="muted">Choose the final lowercase path for this read-only dashboard.</p><label class="field" for="share-path">Blend path<input id="share-path" type="text" autocomplete="off" spellcheck="false" pattern="[a-z0-9-]+"></label><p class="errors" id="share-error" role="alert" hidden></p><div class="share-actions"><button class="share-cancel" id="share-cancel" type="button">Cancel</button><button class="share-submit" id="share-submit" type="button">Confirm and publish</button></div></div></div>'''
    share_script = '' if blend_export else r'''
const shareButton=document.getElementById('share-blend'),sharePanel=document.getElementById('share-panel'),sharePath=document.getElementById('share-path'),shareError=document.getElementById('share-error'),shareCancel=document.getElementById('share-cancel'),shareSubmit=document.getElementById('share-submit');
const defaultSlug=`${DATA.company||'portfolio'}-${DATA.period||'dashboard'}`.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
if(shareButton){shareButton.hidden=!(STATE==='ready'||STATE==='warning')||DATA.reconciliation?.status!=='PASS';shareButton.addEventListener('click',()=>{shareError.hidden=true;sharePath.value=defaultSlug;sharePanel.hidden=false;sharePath.focus();sharePath.select()});shareCancel.addEventListener('click',()=>{sharePanel.hidden=true;shareButton.focus()});shareSubmit.addEventListener('click',async()=>{const slug=sharePath.value.trim();if(!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)){shareError.textContent='Use lowercase letters, numbers, and single dashes.';shareError.hidden=false;sharePath.focus();return}shareSubmit.disabled=true;shareCancel.disabled=true;shareError.hidden=true;const prompt=`Publish this explicitly user-confirmed dashboard to Blend at path ${slug}. Render the read-only Blend export with scripts/render_dashboard.py and call the configured Blend MCP path check followed by upload. Do not upload raw CSV or RESULTS.json. Use visibility sso, access_mode closed, comments_enabled false, and discoverable false. Report the final URL or error.`;if(window.openai?.sendFollowUpMessage){await window.openai.sendFollowUpMessage({title:'Confirm Blend publication',prompt});showToast('Blend publication request sent');sharePanel.hidden=true}else{shareError.textContent='This action must run from an interactive Codex chat dashboard.';shareError.hidden=false;shareSubmit.disabled=false;shareCancel.disabled=false}})}'''
    return (TEMPLATE.replace("__PAYLOAD__", safe_payload)
            .replace("__STATE__", json.dumps(state))
            .replace("__BLEND_EXPORT__", "true" if blend_export else "false")
            .replace("__SHARE_HEADER__", share_header)
            .replace("__SHARE_PANEL__", share_panel)
            .replace("__SHARE_SCRIPT__", share_script))


def render_fragment(payload, state):
    """Return the exact dashboard surface for an in-chat Codex widget."""
    document = render(payload, state)
    style = document.split("<style>", 1)[1].split("</style>", 1)[0]
    body = document.split("<body>", 1)[1].split("</body>", 1)[0]
    return f"<style>{style}</style>{body}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results_json")
    parser.add_argument("--output", required=True)
    parser.add_argument("--blend-export", action="store_true", help="render the read-only Blend distribution view")
    parser.add_argument("--codex-fragment", action="store_true", help="render the same dashboard as an in-chat Codex fragment")
    args = parser.parse_args()
    payload, load_errors = load(args.results_json)
    errors, _ = (load_errors, []) if load_errors else validate(payload)
    state = presentation_state(payload, errors)
    if payload is None:
        payload = {
            "company": None, "period": "Unavailable", "synthetic": False,
            "validation": {"status": "FAIL", "errors": errors, "warnings": []},
            "reconciliation": {"status": "NOT_RUN", "mismatches": []}, "results": [],
        }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if args.blend_export and args.codex_fragment:
        parser.error("--blend-export and --codex-fragment cannot be used together")
    content = render_fragment(payload, state) if args.codex_fragment else render(payload, state, blend_export=args.blend_export)
    output.write_text(content, encoding="utf-8")
    print(output.resolve())
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
