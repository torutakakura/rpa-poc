"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { FileText, Play, ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useState } from "react";

const navigation = [
  { name: "シナリオ", href: "/scenarios", icon: FileText },
  { name: "デモ実行", href: "/demo", icon: Play },
];

export function AppSidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div
      className={cn(
        "relative flex flex-col h-full bg-slate-50 border-r border-slate-200 transition-all duration-300",
        collapsed ? "w-[60px]" : "w-64"
      )}
    >
      <div className="flex items-center justify-between p-4 border-b border-slate-200 bg-white">
        {!collapsed && (
          <h2 className="text-lg font-semibold">RPA Manager</h2>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setCollapsed(!collapsed)}
          className={cn(collapsed && "mx-auto")}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      <nav className="flex-1 p-2">
        <ul className="space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href || 
              (item.href !== "/" && pathname.startsWith(item.href));
            
            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-slate-700 text-white"
                      : "text-slate-600 hover:bg-slate-100 hover:text-slate-800",
                    collapsed && "justify-center px-2"
                  )}
                  title={collapsed ? item.name : undefined}
                >
                  <item.icon className="h-5 w-5 flex-shrink-0" />
                  {!collapsed && <span>{item.name}</span>}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="p-4 border-t border-slate-200 bg-white">
        <div
          className={cn(
            "text-xs text-slate-500",
            collapsed && "text-center"
          )}
        >
          {collapsed ? "v1.0" : "RPA POC v1.0"}
        </div>
      </div>
    </div>
  );
}