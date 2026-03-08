import "./globals.css"
import Navbar from "../components/Navbar"

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html>
      <body className="bg-gray-900 text-white">
        <Navbar />
        <div className="p-6">{children}</div>
      </body>
    </html>
  )
}