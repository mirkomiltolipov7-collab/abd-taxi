import glob, re
from pathlib import Path
files = sorted([Path(f) for f in glob.glob('src/**/*', recursive=True) if Path(f).is_file() and Path(f).suffix in {'.ts', '.tsx'}])
mappings = {
    "fontFamily: 'Syne', sans-serif, color: 'var(--nv)'": 'syne text-nv',
    'fontFamily: "\'Syne\', sans-serif", color: "var(--nv)"': 'syne text-nv',
    'fontFamily: "\'Syne\', sans-serif"': 'syne',
    'color: "var(--mu)"': 'text-mu',
    'color: "var(--or)"': 'text-or',
    'color: "var(--gr)"': 'text-gr',
    'color: "var(--sl)"': 'text-sl',
    'color: "var(--rd)"': 'text-rd',
    'color: "var(--am)"': 'text-am',
    'color: "var(--nv)"': 'text-nv',
    'background: "var(--nv)"': 'bg-nv',
    'background: "var(--or)"': 'bg-or',
    'background: "var(--grb)"': 'bg-grb',
    'background: "var(--orl)"': 'bg-orl',
    'background: "var(--wh)"': 'bg-white',
    'background: "var(--bg)"': 'bg-bg',
    'borderColor: "var(--ln)"': 'border-ln',
    'background: "rgba(232,99,26,.10)"': 'bg-ai-decor',
    'background: "rgba(232,99,26,.06)"': 'bg-ai-decor-soft',
    'background: "rgba(255,255,255,.08)"': 'bg-soft-white',
    'background: "rgba(255,255,255,.15)"': 'bg-white-15',
    'color: "rgba(255,255,255,.5)"': 'text-white-50',
    'color: "rgba(255,255,255,.45)"': 'text-white-45',
    'color: "rgba(255,255,255,.4)"': 'text-white-40',
    'color: "rgba(255,255,255,.7)"': 'text-white-70',
    'color: "rgba(255,255,255,.75)"': 'text-white-75',
    'color: "rgba(255,255,255,.38)"': 'text-white-38',
    'background: "rgba(34,197,94,.15)"': 'bg-soft-green text-[#22C55E]',
    'background: "#22C55E"': 'bg-[#22C55E]',
    'left: 12,': 'left-3 ',
    'top: 12,': 'top-3 ',
    'bottom: 12,': 'bottom-3 ',
    'right: 12,': 'right-3 ',
    'zIndex: 1000,': 'z-[1000] ',
    'background: "rgba(15,27,45,.85)"': 'bg-emphasis',
    'background: "rgba(15,27,45,.7)"': 'bg-emphasis-70',
    'background: "rgba(26,158,92,.8)"': 'bg-success-decor',
    'background: "rgba(255,255,255,.1)"': 'bg-white-10 text-white-80',
    'background: "rgba(255,255,255,.2)"': 'bg-white-20',
    'border: "1px solid var(--ln)"': 'border border-ln',
    'border: "1px solid rgba(255,255,255,.1)"': 'border border-white-10',
    'height: 70,': 'h-[70px] ',
    'width: 68, height: 68,': 'w-[68px] h-[68px] ',
}
pattern = re.compile(r'style=\{\{([^}]+)\}\}')
changes = 0
for path in files:
    text = path.read_text(encoding='utf-8')
    out = text
    for m in pattern.finditer(text):
        body = m.group(1).strip()
        original = m.group(0)
        replaced = body
        added = []
        for key, cls in mappings.items():
            if key in replaced:
                replaced = replaced.replace(key, '')
                added.append(cls)
        rest = ','.join([part.strip() for part in replaced.split(',') if part.strip()])
        if rest == '':
            cls_str = ' '.join(added)
            cm = re.search('className=("[^"]*"|\'[^\']*\')', original)
            if cm and cls_str:
                cls_val = cm.group(1)
                quote = cls_val[0]
                existing = cls_val[1:-1]
                if cls_str in existing:
                    new_cls = existing
                else:
                    new_cls = (existing + ' ' + cls_str).strip()
                new_cls_quoted = quote + new_cls + quote
                replacement = original.replace(cm.group(0), 'className=' + new_cls_quoted)
                out = out.replace(original, replacement)
                changes += 1
    if out != text:
        path.write_text(out, encoding='utf-8')
print('files processed', len(files), 'changes', changes)
