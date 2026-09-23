import { ButtonLink } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
const tools = [["Imports", "/admin/imports"], ["Colleges", "/admin/colleges"], ["Sources", "/admin/sources"], ["Rules", "/admin/rules"], ["System", "/admin/system"]];
export default function AdminPage() { return <div className="mx-auto w-full max-w-5xl px-5 py-12 sm:px-8"><p className="text-sm font-semibold text-primary">Restricted</p><h1 className="mt-2 text-4xl font-bold">Administration</h1><div className="mt-8 grid gap-4 sm:grid-cols-2">{tools.map(([label, href]) => <Card className="flex items-center justify-between p-5" key={href}><h2 className="font-semibold">{label}</h2><ButtonLink href={href} variant="secondary">Open</ButtonLink></Card>)}</div></div>; }
