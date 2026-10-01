#!/usr/bin/env python3
"""Generate contextual paid paths without exporting or sending tool answers."""
import html,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='https://deekeforbusiness.github.io/deekebiz-product-hub/'
KITS={
'contractor-quote-comparison':('Contractor Quote Decision Kit','Keep the written quotes, evidence, questions, and contractor follow-ups together.'),
'used-car-evidence-pack':('Used-Car Seller Evidence Kit','Prepare your vehicle records, evidence, buyer questions, and follow-up notes.'),
'caregiver-handoff-builder':('Family Caregiver Handoff Kit','Organize the family-entered routines, evidence, questions, and handoff follow-ups.'),
'renter-move-in-condition-report':('Renter Move-In Evidence Kit','Keep the condition record, original evidence references, and landlord follow-ups together.'),
'digital-emergency-map':('Digital Emergency Map Kit','Organize record locations, trusted contacts, and questions without recording passwords.'),
'freelancer-scope-creep-checker':('Freelancer Scope Control Kit','Keep the agreed scope, new request, questions, written response, and follow-up together.'),
'insurance-claim-inventory':('Insurance Claim Evidence Kit','Organize original evidence, questions, communications, and claim follow-up records.'),
'home-repair-decision-log':('Home Repair Decision Kit','Keep repair options, supporting evidence, questions, and next actions in one kit.'),
'subscription-cancellation-record':('Subscription Cancellation Evidence Kit','Keep the cancellation evidence, questions, written communications, and follow-up record.'),
'moving-quote-comparison':('Moving Quote Decision Kit','Keep moving quotes, scope questions, supporting evidence, and follow-ups together.')}
for slug,(kit,benefit) in KITS.items():
 path=ROOT/'claritypack10/tools'/slug/'index.html';s=path.read_text()
 ongoing=''
 if slug=='freelancer-scope-creep-checker':
  ongoing=f'''<div class="db-recommendation"><p class="cp-kicker">For ongoing client work</p><h3>Keep the next request with the project.</h3><p>Client Delivery OS is a separate Notion workspace for client pipeline, projects, requests, approvals, meetings, finance items, and renewals.</p><div class="db-actions"><a class="db-link" href="{BASE}client-delivery-os/">See Client Delivery OS — $19+ USD</a></div></div>'''
 summary=f'''<div data-result-upgrade class="db-recommendation"><p class="cp-kicker">Optional next step</p><h3>{kit}</h3><p>For a checklist, question prompts, communication scripts, and a follow-up tracker, this PDF kit is included in the complete ClarityPack10 bundle.</p><p class="db-muted">All ten PDF kits + master guide: $19 USD, one-time. This free browser report remains free.</p><a class="db-link" href="#next-steps">Compare the free tool and the PDF bundle</a></div>'''+ongoing
 if 'data-result-upgrade' not in s:
  s=s.replace('<dl data-report-body></dl>','<dl data-report-body></dl>'+summary,1)
 section=f'''<section class="cp-section" id="next-steps"><div class="cp-wrap"><span class="cp-kicker">Optional deeper workflow</span><h2>Start with the {kit}.</h2><p class="cp-lead">{benefit} This kit is one of the ten PDFs in the $19 bundle.</p><div class="db-comparison-wrap"><table class="db-comparison"><caption>Free browser tool and optional PDF bundle</caption><thead><tr><th scope="col">What you need</th><th scope="col">This free tool</th><th scope="col">ClarityPack10 Pro Bundle · $19</th></tr></thead><tbody><tr><th scope="row">A quick record</th><td>Enter your own facts and print the report.</td><td>Use a printable PDF kit for your situation.</td></tr><tr><th scope="row">A fuller process</th><td>Local draft and report. No account required.</td><td>Evidence checklist, question prompts, ready-to-edit communication scripts, and follow-up tracker.</td></tr><tr><th scope="row">Format</th><td>Browser tool; print or save PDF.</td><td>One ZIP: ten PDF kits and a master start guide. No Notion account or subscription.</td></tr></tbody></table></div><div class="db-actions"><a class="db-link primary" href="https://deekebiz.gumroad.com/l/claritypack10-pro-bundle">Get all 10 PDF kits — $19 USD</a><a class="db-link" href="{BASE}claritypack10/#pro">See the complete bundle contents</a></div>{ongoing}</div></section>'''
 if 'id="next-steps"' in s:
  s=re.sub(r'<section class="cp-section" id="next-steps">.*?</section>',lambda _:section,s,flags=re.S)
 else:
  s=re.sub(r'<section class="cp-section"><div class="cp-wrap"><div class="cp-band">.*?</section>',lambda _:section,s,count=1,flags=re.S)
 if 'class="cp-report-credit"' not in s:
  s=s.replace('<dl data-report-body></dl>','<dl data-report-body></dl><p class="cp-report-credit">Created with ClarityPack10 by DeekeBiz · <a href="'+BASE+'claritypack10/tools/'+slug+'/">'+BASE+'claritypack10/tools/'+slug+'/</a></p>')
 if '<noscript>' not in s:
  s=s.replace('<main id="main">','<noscript><p class="cp-noscript">Enable JavaScript to build a report. You can still read the tool information and bundle contents.</p></noscript><main id="main">')
 path.write_text(s)
print('Connected all 10 tools to their relevant PDF kit; added Client Delivery OS to the scope-change workflow.')
