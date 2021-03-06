#include <lib/gdi/glcddc.h>
#include <lib/gdi/lcd.h>
#include <lib/base/init.h>
#include <lib/base/init_num.h>

gLCDDC *gLCDDC::instance;

gLCDDC::gLCDDC()
{
	lcd = new eDBoxLCD();
	instance=this;
	
	update=1;

	surface.x=lcd->size().width();
	surface.y=lcd->size().height();
	surface.stride=lcd->stride();
	surface.bypp=surface.stride / surface.x;
	surface.bpp=surface.bypp*8;
	surface.data=lcd->buffer();
	surface.clut.colors=0;
	surface.clut.data=0;

	m_pixmap = new gPixmap(&surface);
}

gLCDDC::~gLCDDC()
{
	delete lcd;
	instance=0;
}

void gLCDDC::exec(gOpcode *o)
{
	switch (o->opcode)
	{
#ifdef BUILD_VUPLUS_DUO /* ikseong  */
	case gOpcode::renderText:
		if (o->parm.renderText->text)
		{
			lcd->updates(gDC::m_current_offset,o->parm.renderText->text);
			free(o->parm.renderText->text);
			delete o->parm.renderText;
		}
		break;
#endif			
	case gOpcode::flush:
//		if (update)
#ifndef BUILD_VUPLUS /* ikseong  */
			lcd->update();
#else
			;
#endif
	default:
		gDC::exec(o);
		break;
	}
}

void gLCDDC::setUpdate(int u)
{
	update=u;
}

eAutoInitPtr<gLCDDC> init_gLCDDC(eAutoInitNumbers::graphic-1, "gLCDDC");
