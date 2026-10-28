// Ebb supplement catalog: structure only; names and notes live in i18n/catalog.*.js
// Sources and grading rationale: research/05-supplement-catalog.md
//
// dose  = a common label amount per day (pre-fill only; the user overwrites it).
//         null where one number cannot describe the product (multivitamin, B-complex).
// ul    = adult Tolerable Upper Intake Level per day in the same unit (NIH ODS / NASEM),
//         or null when none is established. Calcium uses the 51+ value (2,000 mg).
// warn  = pairwise interactions. Each pair is listed once; the app should check both
//         directions (A.warn has B, or B.warn has A).
window.EBB_CATALOG = [
  /* --- program items in common forms --- */
  {id:"vit_d3", cat:"vitamins", unit:"IU", dose:2000, ul:4000, slot:"morning", grade:"B", skip:false, replaces:["s_d3"], avoid:["kidney"], warn:[], lab:false},
  {id:"d3_k2", cat:"vitamins", unit:"IU", dose:2000, ul:4000, slot:"morning", grade:"B", skip:false, replaces:["s_d3"], avoid:["thinner","kidney"], warn:[{with:"vit_d3", key:"w_dup"}, {with:"vit_k2", key:"w_dup"}], lab:false},
  {id:"mg_glycinate", cat:"minerals", unit:"mg", dose:200, ul:350, slot:"night", grade:"C", skip:false, replaces:["s_mg"], avoid:["kidney"], warn:[], lab:false},
  {id:"mg_citrate", cat:"minerals", unit:"mg", dose:200, ul:350, slot:"evening", grade:"C", skip:false, replaces:["s_mg"], avoid:["kidney"], warn:[{with:"mg_glycinate", key:"w_dup"}], lab:false},
  {id:"mg_threonate", cat:"minerals", unit:"mg", dose:144, ul:350, slot:"night", grade:"C", skip:false, replaces:["s_mg"], avoid:["kidney"], warn:[{with:"mg_glycinate", key:"w_dup"}, {with:"mg_citrate", key:"w_dup"}], lab:false},
  {id:"fish_oil", cat:"fats", unit:"mg", dose:1000, ul:null, slot:"evening", grade:"B", skip:false, replaces:["s_o3"], avoid:["thinner","heart"], warn:[], lab:false},
  {id:"krill_oil", cat:"fats", unit:"mg", dose:1000, ul:null, slot:"evening", grade:"C", skip:false, replaces:["s_o3"], avoid:["thinner"], warn:[{with:"fish_oil", key:"w_dup"}], lab:false},
  {id:"algal_oil", cat:"fats", unit:"mg", dose:500, ul:null, slot:"evening", grade:"B", skip:false, replaces:["s_o3"], avoid:["thinner"], warn:[{with:"fish_oil", key:"w_dup"}], lab:false},
  {id:"creatine", cat:"sport", unit:"g", dose:5, ul:null, slot:"morning", grade:"A", skip:false, replaces:["s_crea"], avoid:["kidney"], warn:[], lab:true},
  {id:"l_theanine", cat:"sleep", unit:"mg", dose:200, ul:null, slot:"morning", grade:"B", skip:false, replaces:["s_thea"], avoid:["sedative"], warn:[], lab:false},
  {id:"psyllium", cat:"gut", unit:"g", dose:5, ul:null, slot:"midday", grade:"A", skip:false, replaces:["s_psy1","s_psy2"], avoid:["thyroid","diabetes"], warn:[], lab:false},
  {id:"ashwagandha", cat:"herbal", unit:"mg", dose:600, ul:null, slot:"evening", grade:"B", skip:false, replaces:["s_ash"], avoid:["preg","thyroid","liver","autoimmune","sedative"], warn:[], lab:false},
  {id:"probiotic", cat:"gut", unit:"bn CFU", dose:10, ul:null, slot:"morning", grade:"C", skip:false, replaces:["s_pro"], avoid:[], warn:[], lab:false},
  {id:"saffron", cat:"herbal", unit:"mg", dose:30, ul:null, slot:"morning", grade:"B", skip:false, replaces:["s_saf"], avoid:["preg","ssri","thinner"], warn:[{with:"rhodiola", key:"w_serotonin"}, {with:"st_johns_wort", key:"w_serotonin"}], lab:false},
  {id:"glycine", cat:"sleep", unit:"g", dose:3, ul:null, slot:"night", grade:"C", skip:false, replaces:["s_gly"], avoid:[], warn:[], lab:false},

  /* --- vitamins --- */
  {id:"multivitamin", cat:"vitamins", unit:"mg", dose:null, ul:null, slot:"morning", grade:"C", skip:false, replaces:[], avoid:[], warn:[{with:"vit_a", key:"w_dup"}, {with:"vit_e", key:"w_dup"}, {with:"zinc", key:"w_dup"}, {with:"iron", key:"w_dup"}, {with:"b_complex", key:"w_dup"}, {with:"folate", key:"w_dup"}, {with:"selenium", key:"w_dup"}, {with:"iodine", key:"w_dup"}, {with:"vit_d3", key:"w_dup"}, {with:"s_d3", key:"w_dup"}], lab:false},
  {id:"vit_c", cat:"vitamins", unit:"mg", dose:500, ul:2000, slot:"morning", grade:"C", skip:false, replaces:[], avoid:["kidney"], warn:[], lab:true},
  {id:"b_complex", cat:"vitamins", unit:"mg", dose:null, ul:null, slot:"morning", grade:"C", skip:false, replaces:[], avoid:[], warn:[{with:"vit_b12", key:"w_dup"}, {with:"folate", key:"w_dup"}, {with:"biotin", key:"w_dup"}], lab:true},
  {id:"vit_b12", cat:"vitamins", unit:"µg", dose:1000, ul:null, slot:"morning", grade:"B", skip:false, replaces:[], avoid:[], warn:[], lab:false},
  {id:"folate", cat:"vitamins", unit:"µg", dose:400, ul:1000, slot:"morning", grade:"B", skip:false, replaces:[], avoid:[], warn:[], lab:false},
  {id:"biotin", cat:"vitamins", unit:"µg", dose:5000, ul:null, slot:"morning", grade:"D", skip:false, replaces:[], avoid:["thyroid","heart"], warn:[], lab:true},
  {id:"vit_k2", cat:"vitamins", unit:"µg", dose:100, ul:null, slot:"morning", grade:"C", skip:false, replaces:[], avoid:["thinner"], warn:[{with:"s_d3", key:"w_dup"}], lab:false},
  {id:"vit_e", cat:"vitamins", unit:"mg", dose:268, ul:1000, slot:"evening", grade:"D", skip:false, replaces:[], avoid:["thinner"], warn:[{with:"fish_oil", key:"w_bleed"}, {with:"s_o3", key:"w_bleed"}], lab:false},
  {id:"vit_a", cat:"vitamins", unit:"µg", dose:1500, ul:3000, slot:"morning", grade:"D", skip:false, replaces:[], avoid:["preg","liver"], warn:[], lab:false},

  /* --- minerals --- */
  {id:"zinc", cat:"minerals", unit:"mg", dose:25, ul:40, slot:"evening", grade:"C", skip:false, replaces:[], avoid:[], warn:[{with:"copper", key:"w_copper"}], lab:false},
  {id:"copper", cat:"minerals", unit:"mg", dose:2, ul:10, slot:"midday", grade:"C", skip:false, replaces:[], avoid:["liver"], warn:[], lab:false},
  {id:"iron", cat:"minerals", unit:"mg", dose:18, ul:45, slot:"morning", grade:"B", skip:false, replaces:[], avoid:["liver"], warn:[{with:"calcium", key:"w_absorb"}, {with:"s_psy1", key:"w_absorb"}, {with:"psyllium", key:"w_absorb"}, {with:"zinc", key:"w_absorb"}], lab:false},
  {id:"calcium", cat:"minerals", unit:"mg", dose:600, ul:2000, slot:"evening", grade:"B", skip:false, replaces:[], avoid:["kidney","heart","thyroid"], warn:[{with:"zinc", key:"w_absorb"}], lab:false},
  {id:"selenium", cat:"minerals", unit:"µg", dose:200, ul:400, slot:"morning", grade:"D", skip:false, replaces:[], avoid:["diabetes"], warn:[], lab:false},
  {id:"iodine", cat:"minerals", unit:"µg", dose:150, ul:1100, slot:"morning", grade:"C", skip:false, replaces:[], avoid:["thyroid"], warn:[{with:"s_ash", key:"w_thyroid"}, {with:"ashwagandha", key:"w_thyroid"}], lab:false},
  {id:"electrolytes", cat:"minerals", unit:"mg", dose:200, ul:null, slot:"midday", grade:"C", skip:false, replaces:[], avoid:["kidney","heart"], warn:[], lab:false},
  {id:"chromium", cat:"minerals", unit:"µg", dose:200, ul:null, slot:"midday", grade:"D", skip:true, replaces:[], avoid:["kidney","liver","diabetes"], warn:[{with:"berberine", key:"w_sugar"}], lab:false},

  /* --- joints and skin --- */
  {id:"collagen", cat:"joints", unit:"g", dose:10, ul:null, slot:"morning", grade:"C", skip:false, replaces:[], avoid:[], warn:[], lab:false},
  {id:"glucosamine", cat:"joints", unit:"mg", dose:1500, ul:null, slot:"morning", grade:"C", skip:false, replaces:[], avoid:["thinner"], warn:[], lab:false},

  /* --- energy and longevity --- */
  {id:"coq10", cat:"longevity", unit:"mg", dose:100, ul:null, slot:"morning", grade:"C", skip:false, replaces:[], avoid:["thinner"], warn:[], lab:false},
  {id:"pqq", cat:"longevity", unit:"mg", dose:20, ul:null, slot:"morning", grade:"D", skip:false, replaces:[], avoid:[], warn:[], lab:false},
  {id:"nac", cat:"longevity", unit:"mg", dose:600, ul:null, slot:"morning", grade:"C", skip:false, replaces:[], avoid:[], warn:[], lab:false},
  {id:"glutathione", cat:"longevity", unit:"mg", dose:250, ul:null, slot:"morning", grade:"D", skip:false, replaces:[], avoid:[], warn:[], lab:false},
  {id:"ala", cat:"longevity", unit:"mg", dose:600, ul:null, slot:"morning", grade:"C", skip:false, replaces:[], avoid:["diabetes"], warn:[{with:"berberine", key:"w_sugar"}], lab:false},
  {id:"nmn", cat:"longevity", unit:"mg", dose:500, ul:null, slot:"morning", grade:"D", skip:true, replaces:[], avoid:[], warn:[{with:"nr", key:"w_dup"}], lab:false},
  {id:"nr", cat:"longevity", unit:"mg", dose:300, ul:null, slot:"morning", grade:"D", skip:true, replaces:[], avoid:[], warn:[], lab:false},
  {id:"resveratrol", cat:"longevity", unit:"mg", dose:250, ul:null, slot:"morning", grade:"D", skip:true, replaces:[], avoid:["thinner"], warn:[], lab:false},
  {id:"quercetin", cat:"longevity", unit:"mg", dose:500, ul:null, slot:"morning", grade:"C", skip:false, replaces:[], avoid:[], warn:[], lab:false},
  {id:"fisetin", cat:"longevity", unit:"mg", dose:100, ul:null, slot:"morning", grade:"D", skip:false, replaces:[], avoid:[], warn:[], lab:false},
  {id:"spermidine", cat:"longevity", unit:"mg", dose:1, ul:null, slot:"morning", grade:"D", skip:false, replaces:[], avoid:[], warn:[], lab:false},
  {id:"urolithin_a", cat:"longevity", unit:"mg", dose:500, ul:null, slot:"morning", grade:"C", skip:false, replaces:[], avoid:[], warn:[], lab:false},
  {id:"astaxanthin", cat:"longevity", unit:"mg", dose:12, ul:null, slot:"midday", grade:"C", skip:false, replaces:[], avoid:[], warn:[], lab:false},
  {id:"tmg", cat:"longevity", unit:"g", dose:1, ul:null, slot:"morning", grade:"C", skip:false, replaces:[], avoid:["heart"], warn:[], lab:false},
  {id:"taurine", cat:"longevity", unit:"g", dose:2, ul:null, slot:"evening", grade:"C", skip:false, replaces:[], avoid:[], warn:[], lab:false},
  {id:"l_carnitine", cat:"longevity", unit:"mg", dose:1000, ul:null, slot:"morning", grade:"C", skip:false, replaces:[], avoid:["thyroid"], warn:[], lab:false},

  /* --- metabolic and blood sugar --- */
  {id:"berberine", cat:"metabolic", unit:"mg", dose:1000, ul:null, slot:"midday", grade:"B", skip:false, replaces:[], avoid:["preg","diabetes","thinner","ssri"], warn:[{with:"red_yeast_rice", key:"w_statin"}, {with:"myo_inositol", key:"w_sugar"}], lab:false},
  {id:"myo_inositol", cat:"metabolic", unit:"g", dose:2, ul:null, slot:"morning", grade:"B", skip:false, replaces:[], avoid:["diabetes"], warn:[], lab:false},
  {id:"red_yeast_rice", cat:"metabolic", unit:"mg", dose:1200, ul:null, slot:"evening", grade:"B", skip:false, replaces:[], avoid:["preg","liver","kidney"], warn:[{with:"s_ash", key:"w_liver"}, {with:"ashwagandha", key:"w_liver"}], lab:false},

  /* --- sleep and calm --- */
  {id:"melatonin", cat:"sleep", unit:"mg", dose:3, ul:null, slot:"night", grade:"B", skip:false, replaces:[], avoid:["preg","sedative","autoimmune"], warn:[{with:"s_ash", key:"w_sedation"}, {with:"ashwagandha", key:"w_sedation"}, {with:"lemon_balm", key:"w_sedation"}, {with:"apigenin", key:"w_sedation"}], lab:false},
  {id:"rhodiola", cat:"herbal", unit:"mg", dose:400, ul:null, slot:"morning", grade:"C", skip:false, replaces:[], avoid:["ssri","preg"], warn:[{with:"s_saf", key:"w_serotonin"}, {with:"caffeine", key:"w_stim"}], lab:false},
  {id:"holy_basil", cat:"herbal", unit:"mg", dose:250, ul:null, slot:"morning", grade:"C", skip:false, replaces:[], avoid:["preg","thinner","diabetes"], warn:[], lab:false},
  {id:"apigenin", cat:"sleep", unit:"mg", dose:50, ul:null, slot:"night", grade:"C", skip:false, replaces:[], avoid:["sedative"], warn:[], lab:false},
  {id:"lemon_balm", cat:"sleep", unit:"mg", dose:500, ul:null, slot:"evening", grade:"C", skip:false, replaces:[], avoid:["sedative","thyroid"], warn:[{with:"s_ash", key:"w_sedation"}, {with:"ashwagandha", key:"w_sedation"}], lab:false},

  /* --- brain --- */
  {id:"lions_mane", cat:"brain", unit:"mg", dose:1000, ul:null, slot:"morning", grade:"C", skip:false, replaces:[], avoid:[], warn:[], lab:false},
  {id:"alpha_gpc", cat:"brain", unit:"mg", dose:600, ul:null, slot:"morning", grade:"C", skip:false, replaces:[], avoid:["heart"], warn:[], lab:false},
  {id:"ginkgo", cat:"brain", unit:"mg", dose:240, ul:null, slot:"morning", grade:"D", skip:false, replaces:[], avoid:["thinner"], warn:[{with:"fish_oil", key:"w_bleed"}, {with:"krill_oil", key:"w_bleed"}, {with:"algal_oil", key:"w_bleed"}, {with:"s_o3", key:"w_bleed"}, {with:"turmeric", key:"w_bleed"}, {with:"vit_e", key:"w_bleed"}], lab:false},
  {id:"methylene_blue", cat:"brain", unit:"mg", dose:10, ul:null, slot:"morning", grade:"D", skip:true, replaces:[], avoid:["ssri","preg"], warn:[{with:"s_saf", key:"w_serotonin"}, {with:"saffron", key:"w_serotonin"}, {with:"st_johns_wort", key:"w_serotonin"}, {with:"rhodiola", key:"w_serotonin"}], lab:false},

  /* --- anti-inflammatory --- */
  {id:"turmeric", cat:"joints", unit:"mg", dose:500, ul:null, slot:"midday", grade:"B", skip:false, replaces:[], avoid:["thinner","liver"], warn:[{with:"s_ash", key:"w_liver"}, {with:"ashwagandha", key:"w_liver"}], lab:false},

  /* --- sport --- */
  {id:"mct_oil", cat:"sport", unit:"g", dose:15, ul:null, slot:"morning", grade:"C", skip:false, replaces:[], avoid:[], warn:[], lab:false},
  {id:"caffeine", cat:"sport", unit:"mg", dose:200, ul:null, slot:"morning", grade:"A", skip:false, replaces:[], avoid:["heart","preg"], warn:[{with:"red_ginseng", key:"w_stim"}, {with:"green_tea_extract", key:"w_stim"}], lab:false},
  {id:"beetroot", cat:"sport", unit:"mg", dose:400, ul:null, slot:"morning", grade:"B", skip:false, replaces:[], avoid:[], warn:[{with:"citrulline", key:"w_bp"}], lab:false},
  {id:"citrulline", cat:"sport", unit:"g", dose:6, ul:null, slot:"midday", grade:"C", skip:false, replaces:[], avoid:[], warn:[], lab:false},
  {id:"whey", cat:"sport", unit:"g", dose:25, ul:null, slot:"midday", grade:"A", skip:false, replaces:[], avoid:["kidney"], warn:[], lab:false},

  /* --- herbal, men, eyes --- */
  {id:"st_johns_wort", cat:"herbal", unit:"mg", dose:900, ul:null, slot:"morning", grade:"B", skip:true, replaces:[], avoid:["ssri","thinner","heart","preg"], warn:[{with:"s_saf", key:"w_serotonin"}, {with:"rhodiola", key:"w_serotonin"}], lab:false},
  {id:"saw_palmetto", cat:"men", unit:"mg", dose:320, ul:null, slot:"evening", grade:"D", skip:false, replaces:[], avoid:["thinner"], warn:[], lab:false},
  {id:"lutein", cat:"eyes", unit:"mg", dose:20, ul:null, slot:"midday", grade:"B", skip:false, replaces:[], avoid:[], warn:[], lab:false},

  /* --- Korea-popular --- */
  {id:"red_ginseng", cat:"herbal", unit:"mg", dose:3000, ul:null, slot:"morning", grade:"C", skip:false, replaces:[], avoid:["thinner","diabetes","preg"], warn:[], lab:false},
  {id:"milk_thistle", cat:"herbal", unit:"mg", dose:130, ul:null, slot:"morning", grade:"C", skip:false, replaces:[], avoid:["diabetes"], warn:[], lab:false},
  {id:"propolis", cat:"herbal", unit:"mg", dose:500, ul:null, slot:"morning", grade:"C", skip:false, replaces:[], avoid:["thinner"], warn:[], lab:false},

  /* --- skip list --- */
  {id:"green_tea_extract", cat:"metabolic", unit:"mg", dose:500, ul:null, slot:"morning", grade:"C", skip:true, replaces:[], avoid:["liver","preg"], warn:[{with:"s_ash", key:"w_liver"}, {with:"ashwagandha", key:"w_liver"}, {with:"turmeric", key:"w_liver"}], lab:false},
  {id:"cla", cat:"metabolic", unit:"mg", dose:3000, ul:null, slot:"midday", grade:"D", skip:true, replaces:[], avoid:["diabetes"], warn:[], lab:false},
  {id:"acv", cat:"metabolic", unit:"mg", dose:1000, ul:null, slot:"midday", grade:"D", skip:true, replaces:[], avoid:["diabetes"], warn:[], lab:false},
  {id:"garcinia", cat:"metabolic", unit:"mg", dose:1500, ul:null, slot:"midday", grade:"D", skip:true, replaces:[], avoid:["liver","ssri"], warn:[{with:"s_ash", key:"w_liver"}, {with:"ashwagandha", key:"w_liver"}], lab:false},
  {id:"dhea", cat:"men", unit:"mg", dose:25, ul:null, slot:"morning", grade:"C", skip:true, replaces:[], avoid:["preg","liver"], warn:[], lab:true}
];
