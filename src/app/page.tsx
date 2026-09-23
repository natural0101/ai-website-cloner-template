export default function Home() {
  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <div className="max-w-xl space-y-4">
        <h1 className="text-3xl font-semibold tracking-tight">Website Cloner</h1>
        <p className="text-muted-foreground">
          Отправьте агенту ссылку на сайт, который хотите скопировать.
          Шаблон готов к новой задаче.
        </p>
      </div>
    </main>
  );
}