import re
import json

HTML_PATH = "Trade overview.html"

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Bug Fix for Identical Brand Names
if "marksMap.get(brand).grades[variety] = {" in html:
    html = html.replace("if (!marksMap.has(brand)) marksMap.set(brand, { id: `m-${idx}`, name: brand, grades: {} });", "")
    html = html.replace(
        "marksMap.get(brand).grades[variety] = {",
        "let key = brand;\n          while (marksMap.has(key) && marksMap.get(key).grades[variety] !== undefined) {\n             key += '\\u200B';\n          }\n          if (!marksMap.has(key)) marksMap.set(key, { id: `m-${idx}`, name: key, grades: {} });\n          \n          marksMap.get(key).grades[variety] = {"
    )
    html = html.replace("brand: bn", "brand: bn.replace(/\\u200B/g, '')")

# 2. Navbar Refresh Button + Filter Alignment
refresh_btn_code = """<button onClick={sync} disabled={syncing}
                      className="h-10 px-4 bg-white border border-slate-200 rounded-lg text-sm font-bold text-slate-600 hover:text-emerald-600 hover:border-emerald-300 transition-all flex items-center gap-2 shadow-sm active:scale-95 disabled:opacity-50 min-w[110px]">
                      {syncing ? <span className="animate-spin text-lg leading-none">↻</span> : <span className="text-lg leading-none">↻</span>}
                      {syncing ? 'Syncing…' : 'Refresh'}
                    </button>"""
if refresh_btn_code in html: html = html.replace(refresh_btn_code, "")
html = html.replace(
    "{['fleet', 'view'].map(t => (",
    """<button onClick={sync} disabled={syncing} title="Refresh Data"
                      className="flex items-center justify-center w-8 h-8 rounded-md text-slate-500 hover:bg-slate-200 hover:text-slate-800 transition-all mr-1 disabled:opacity-50">
                      <span className={`text-lg leading-none ${syncing ? 'animate-spin' : ''}`}>↻</span>
                    </button>
                    {['fleet', 'view'].map(t => ("""
)
html = html.replace(
    r'<div className="flex flex-wrap items-center gap-2 w-full sm:w-auto mt-4 sm:mt-0">',
    r'<div className="flex flex-wrap items-center gap-3 w-full sm:w-auto mt-4 sm:mt-0 max-w-full">'
)

# 3. Rework Customer Assignment Flow (Customer -> Brands)
panel_pattern = re.compile(r"<!-- ── CUSTOMER ASSIGNMENT PANEL ── -->.*?(?=<!-- ── MEDIA GALLERY ── -->)", re.DOTALL)
new_panel_jsx = r"""<!-- ── CUSTOMER ASSIGNMENT PANEL ── -->
                <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden fade-in">
                  <div className="px-5 py-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
                    <div>
                      <h3 className="font-black text-slate-800 flex items-center gap-2">
                        <span className="text-xl">👥</span> Customer Assignments
                      </h3>
                      <p className="text-xs text-slate-500 font-medium mt-0.5">Assign brands and quantities to specific customers for this trip.</p>
                    </div>
                  </div>
                  <div className="p-5 space-y-5">
                    {/* List of Customers */}
                    {(Array.isArray(brandAssignments) ? brandAssignments : []).map((assignment, cIdx) => (
                      <div key={cIdx} className="bg-white border text-sm border-slate-200 rounded-xl overflow-hidden shadow-sm">
                        <div className="bg-slate-50 px-4 py-3 border-b border-slate-100 flex items-center justify-between gap-3">
                          <input type="text" placeholder="Customer Name..." value={assignment.customer || ''}
                            onChange={e => {
                              const newList = [...brandAssignments];
                              newList[cIdx].customer = e.target.value;
                              saveCustomerAssignments(newList);
                            }}
                            className="bg-white font-bold text-indigo-700 placeholder-indigo-300 border border-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-400 w-full max-w-xs shadow-sm"
                          />
                          <button onClick={() => { const newList = [...brandAssignments]; newList.splice(cIdx, 1); saveCustomerAssignments(newList); }}
                            className="text-red-400 hover:text-red-600 hover:bg-red-50 p-1.5 rounded-lg transition-colors font-bold text-xs">✕ Remove</button>
                        </div>
                        <div className="p-4 space-y-3">
                          {assignment.brands && assignment.brands.length > 0 && (
                            <table className="w-full text-left text-sm border-collapse">
                              <thead><tr className="text-[10px] uppercase text-slate-400 font-bold border-b border-slate-100"><th className="pb-2">Brand / Mark</th><th className="pb-2 text-right">Boxes</th><th className="pb-2"></th></tr></thead>
                              <tbody>
                                {assignment.brands.map((bInfo, bIdx) => (
                                  <tr key={bIdx} className="hover:bg-slate-50/50">
                                    <td className="py-2">
                                      <select value={bInfo.name || ''} onChange={e => { const newList = JSON.parse(JSON.stringify(brandAssignments)); newList[cIdx].brands[bIdx].name = e.target.value; saveCustomerAssignments(newList); }}
                                        className="h-8 max-w-[200px] border border-slate-200 rounded-lg px-2 text-xs font-semibold focus:outline-none focus:border-indigo-400">
                                        <option value="" disabled>Select brand...</option>
                                        {trip.marks.map((m, mIdx) => <option key={mIdx} value={m.name}>{m.name.replace(/\u200B/g, '')} - {Object.values(m.grades).reduce((sum, g) => sum + g.manifest, 0)}</option>)}
                                      </select>
                                    </td>
                                    <td className="py-2 text-right"><input type="number" placeholder="Boxes" value={bInfo.boxes === null ? '' : bInfo.boxes}
                                        onChange={e => { const newList = JSON.parse(JSON.stringify(brandAssignments)); const v = e.target.value; newList[cIdx].brands[bIdx].boxes = v === '' ? null : parseInt(v, 10); saveCustomerAssignments(newList); }}
                                        className="w-20 h-8 text-right text-xs font-bold border rounded px-2 focus:outline-none focus:border-indigo-400" /></td>
                                    <td className="py-2 text-center text-red-300 hover:text-red-500 cursor-pointer text-lg leading-none" onClick={() => { const newList = JSON.parse(JSON.stringify(brandAssignments)); newList[cIdx].brands.splice(bIdx, 1); saveCustomerAssignments(newList); }}>×</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          )}
                          <button onClick={() => { const newList = JSON.parse(JSON.stringify(Array.isArray(brandAssignments) ? brandAssignments : [])); newList[cIdx].brands = newList[cIdx].brands || []; newList[cIdx].brands.push({ name: '', boxes: null }); saveCustomerAssignments(newList); }}
                            className="text-[11px] font-bold text-indigo-600 bg-indigo-50 hover:bg-indigo-100 px-3 py-1.5 rounded-lg border transition-colors">+ Add Brand</button>
                        </div>
                      </div>
                    ))}
                    <button onClick={() => { const newList = Array.isArray(brandAssignments) ? [...brandAssignments] : []; newList.push({ customer: '', brands: [] }); saveCustomerAssignments(newList); }}
                      className="w-full py-3 border-2 border-dashed border-slate-200 rounded-xl text-slate-500 font-bold hover:text-emerald-600 hover:bg-emerald-50 transition-all grid place-items-center">+ Add New Customer</button>
                    
                    {Object.keys(trip.marks).length > 0 && (
                      <div className="mt-6 bg-slate-100/50 border border-slate-200 rounded-xl p-4">
                        <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3">Unallocated Balance</div>
                        <div className="flex flex-wrap gap-2">
                          {trip.marks.map((mk, idx) => {
                            const totalBoxesStr = Object.values(mk.grades).reduce((sum, g) => sum + g.manifest, 0);
                            const totalBoxes = parseInt(totalBoxesStr, 10) || 0;
                            let assignedBoxes = 0;
                            (Array.isArray(brandAssignments) ? brandAssignments : []).forEach(cust => (cust.brands || []).forEach(b => { if (b.name === mk.name && b.boxes) assignedBoxes += b.boxes; }));
                            const unallocated = totalBoxes - assignedBoxes;
                            const isFullyAssigned = unallocated <= 0;
                            return (
                              <div key={idx} className={`text-xs px-2.5 py-1 rounded border flex gap-1.5 ${isFullyAssigned ? 'bg-emerald-50 text-emerald-700' : assignedBoxes > 0 ? 'bg-amber-50 text-amber-700' : 'bg-white text-slate-600'}`}>
                                <span className="font-bold">{mk.name.replace(/\u200B/g, '')}</span>
                                <span className={`px-1 rounded text-[10px] font-bold ${isFullyAssigned ? 'bg-emerald-100' : 'bg-slate-100'}`}>{isFullyAssigned ? '✓ Fully Assigned' : `${unallocated} left`}</span>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                """
html = panel_pattern.sub(new_panel_jsx, html)
html = html.replace("return p._customerAssignments || {};", "return Array.isArray(p._customerAssignments) ? p._customerAssignments : [];")
html = html.replace("setBrandAssignments(p._customerAssignments || {});", "setBrandAssignments(Array.isArray(p._customerAssignments) ? p._customerAssignments : []);")


# 4. Refactoring PDF Generaton to use Hidden Rich-UI Capture
html = html.replace("""{Object.keys(brandAssignments).length > 0 && (
                      <button onClick={downloadCustomerPdfs} disabled={custPdfExporting || exportingType} className="px-4 py-1.5 bg-violet-50 text-violet-700 hover:bg-violet-100 font-bold text-[10px] uppercase tracking-widest rounded-lg flex items-center gap-2 transition-colors border border-violet-200 shadow-sm active:scale-95 disabled:opacity-50 min-w-[130px] justify-center">
                        {custPdfExporting ? <span className="animate-spin tracking-normal text-sm leading-none">↻</span> : <span className="text-sm tracking-normal">👥</span>} {custPdfExporting ? 'Exporting...' : 'Per-Customer PDF'}
                      </button>
                    )}""", "")
html = html.replace("disabled={exportingType || custPdfExporting}", "disabled={exportingType}")

modal_btn_target = """<button onClick={() => handleDownloadExport('PDF')} className="px-6 py-2.5 text-sm font-bold text-white bg-rose-600 hover:bg-rose-700 rounded-xl transition-all shadow-md active:scale-95 flex items-center gap-2">
                      <span>📄</span> Download PDF
                    </button>
                  </div>"""
new_modal_btns = """<button onClick={() => handleDownloadExport('PDF')} className="px-6 py-2.5 text-sm font-bold text-white bg-rose-600 hover:bg-rose-700 rounded-xl transition-all shadow-md active:scale-95 flex items-center gap-2 border">
                      <span>📄</span> Full Manifest PDF
                    </button>
                    {(Array.isArray(brandAssignments) ? brandAssignments : []).filter(c => c.customer && c.brands && c.brands.length > 0).map((cust, i) => (
                      <button key={i} onClick={() => captureHiddenCustomerPdf(cust)} disabled={custPdfExporting === cust.customer} 
                        className="px-6 py-2.5 text-sm font-bold text-violet-700 bg-violet-100 hover:bg-violet-200 rounded-xl transition-all shadow-sm active:scale-95 flex items-center gap-2 border disabled:opacity-50">
                        {custPdfExporting === cust.customer ? <span className="animate-spin text-lg leading-none">↻</span> : <span>📄</span>} 
                        {custPdfExporting === cust.customer ? 'Generating...' : `PDF: ${cust.customer.substring(0, 15)}`}
                      </button>
                    ))}
                  </div>"""
html = html.replace(modal_btn_target, new_modal_btns)

old_dl_regex = re.compile(r"const downloadCustomerPdfs = async \(\) => \{.+?catch\(e\) { setSaveMsg\('❌ PDF failed: ' \+ \(e\.message \|\| ''\)\); }\s+finally { setCustPdfExporting\(false\); }\s+};", re.DOTALL)
new_capture_func = r"""const [custPdfData, setCustPdfData] = useState(null);
      const captureHiddenCustomerPdf = async (customerObj) => {
        setCustPdfExporting(customerObj.customer);
        setCustPdfData(customerObj);
        await new Promise(r => setTimeout(r, 100)); // wait render
        const el = document.getElementById('hidden-customer-export-container');
        if (!el) return;
        try {
          const canvas = await window.html2canvas(el, { scale: 2, backgroundColor: '#F8FAFC', width: 1000, windowWidth: 1000, onclone: doc => doc.body.classList.add('export-mode') });
          const o = canvas.width > canvas.height ? 'l' : 'p';
          const pdf = new window.jspdf.jsPDF(o, 'mm', 'a4');
          pdf.addImage(canvas.toDataURL('image/jpeg', 0.9), 'JPEG', 0, 10, pdf.internal.pageSize.getWidth(), (canvas.height * pdf.internal.pageSize.getWidth()) / canvas.width);
          pdf.save(`Manifest_${localDetails.tripId}_${customerObj.customer.replace(/\s+/g,'_')}.pdf`);
          setSaveMsg(`✓ Downloaded PDF for ${customerObj.customer}`);
          setTimeout(() => setSaveMsg(''), 4000);
        } catch (e) { console.error(e); } finally { setCustPdfExporting(false); setCustPdfData(null); }
      };"""
html = old_dl_regex.sub(new_capture_func, html)

hidden_container = r"""{custPdfData && (
            <div className="absolute top-0 left-[-9999px] z-0 bg-[#F8FAFC] w-[1000px] p-8 shadow-xl">
              <div id="hidden-customer-export-container" className="bg-[#F8FAFC] rounded-xl space-y-6 block p-4 shadow-sm border border-slate-200">
                <div className="text-center mb-4 pt-2 pb-4 border-b-2 border-slate-200">
                  <div className="text-xl font-black text-slate-800 uppercase tracking-widest mt-3">Customer Manifest</div>
                  <div className="text-sm font-bold text-indigo-600 uppercase tracking-widest mt-1">Bill To: {custPdfData.customer}</div>
                </div>
                <div className="space-y-4 pt-2">
                  <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden break-inside-avoid shadow-sm">
                    <div className="grid grid-cols-2 divide-x divide-slate-100 p-5">
                      <div className="flex gap-4"><div className="text-3xl">🛻</div><div><p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-tight">Trip Details</p><p className="font-bold text-slate-800 text-lg leading-tight mt-1">{localDetails.tripId}</p><p className="font-bold text-slate-500 text-sm mt-0.5">{localDetails.vehicleNo}</p></div></div>
                      <div className="flex gap-4 pl-5"><div className="text-3xl">📍</div><div><p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-tight">Route</p><p className="font-bold text-slate-800 text-lg leading-tight mt-1">{localDetails.origin} <span className="text-slate-300">→</span> {localDetails.destination}</p><p className="font-bold text-emerald-600 text-sm mt-0.5 whitespace-nowrap">📅 {fmtDate(localDetails.dispatchDate)}</p></div></div>
                    </div>
                  </div>
                  <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden break-inside-avoid">
                    <div className="px-5 py-3 bg-slate-800 text-white flex justify-between items-center"><h4 className="font-black text-sm uppercase tracking-widest text-slate-200">Assigned Inventory</h4><span className="text-xs font-bold bg-white/20 px-3 py-1 rounded-full">{custPdfData.brands.reduce((s, b) => s + (parseInt(b.boxes)||0), 0)} Total Boxes</span></div>
                    <table className="w-full text-left font-semibold"><thead className="bg-slate-50 text-[11px] uppercase tracking-wider text-slate-500 border-b border-slate-200"><tr><th className="py-3 px-5">Brand / Mark</th><th className="py-3 px-5 text-right w-40">Assigned Quantity</th></tr></thead><tbody className="divide-y divide-slate-100 text-slate-800">{custPdfData.brands.map((b, i) => (<tr key={i} className="hover:bg-slate-50"><td className="py-4 px-5 text-sm font-bold border-r border-slate-50">{b.name.replace(/\u200B/g, '')}</td><td className="py-4 px-5 text-right text-base font-black bg-emerald-50 text-emerald-800">{parseInt(b.boxes)||0} 📦</td></tr>))}</tbody></table>
                  </div>
                </div>
              </div>
            </div>
          )}"""
html = html.replace("{/* Export Preview Modal */}", hidden_container + "\n{/* Export Preview Modal */}")

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)
print("Patching successful.")
