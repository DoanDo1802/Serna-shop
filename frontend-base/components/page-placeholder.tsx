interface PagePlaceholderProps {
  title: string
  description?: string
}

export function PagePlaceholder({
  title,
  description = 'Trang này đã được tạo nhưng hiện đang để trống.',
}: PagePlaceholderProps) {
  return (
    <div className="flex-1 flex items-center justify-center bg-background px-8">
      <div className="max-w-md text-center">
        <h2 className="text-3xl font-bold text-foreground">{title}</h2>
        <p className="mt-3 text-sm text-muted-foreground">{description}</p>
      </div>
    </div>
  )
}